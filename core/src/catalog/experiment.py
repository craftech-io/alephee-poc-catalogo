"""Run a version of the catalog agent as a Langfuse experiment.

    scripts/experiment.sh --version v1 --data mock
    scripts/experiment.sh --version current --data real      # today's process, no model
    scripts/experiment.sh --version v1 --data real --case error-88904447
"""

import argparse
import os
import subprocess

import boto3

from .data import data_dir, load_cases, load_schemas
from .evaluation import make_item_evaluator, make_run_evaluator
from .llm import create_llm
from .prompts import PROMPT_NAME, get_system_prompt, sync_seed
from .tracing import setup_tracing
from .v1 import MappingV1

DATASETS = {"real": "alephee-shopee-real", "mock": "alephee-shopee-mock"}
MAX_CONCURRENCY = 4


def dataset_items(cases: list[dict], origin: str) -> list[dict]:
    name = DATASETS[origin]
    return [{
        "id": f"{name}-{case['id']}",
        "input": case["product"],
        "expected_output": {k: case["expected"][k] for k in ("category", "attributes", "missing", "rejected")},
        "metadata": {"case": case["id"], "origin": origin, "expected_is_mock": True,
                     "decision_pending": case.get("decision_pendiente"), "actual": case.get("actual")},
    } for case in cases]


def upload_dataset(client, origin: str, cases: list[dict]) -> None:
    """Create the dataset if needed and upsert its items by id: re-uploading never duplicates."""
    try:
        client.get_dataset(DATASETS[origin])
    except Exception:  # noqa: BLE001 — the SDK raises a generic API error for "not found"
        client.create_dataset(name=DATASETS[origin],
                              description=f"War room Alephee × Shopee ({origin}); expected outputs are MOCK")
    for item in dataset_items(cases, origin):
        client.create_dataset_item(dataset_name=DATASETS[origin], **item)


def current_task(*, item, **kwargs) -> dict:
    """Today's Alephee listing in the agent contract. It never reports missing attributes."""
    actual = (item.metadata or {}).get("actual")
    if not actual:
        return {"error": "the case has no current listing (mock dataset)"}
    return {"category": actual["category"], "missing": [], "rejected": [],
            "attributes": [{k: a.get(k) for k in ("urn", "valueId", "value", "unit")} for a in actual["attributes"]]}


def make_v1_task(llm, system_prompt: str, schemas: dict[str, dict], workflow_cls=MappingV1):
    async def task(*, item, **kwargs) -> dict:
        done = await workflow_cls(llm=llm, system_prompt=system_prompt, schemas=schemas, timeout=180).run(
            product=item.input)
        return done.listing.model_dump() if done.listing is not None else {"error": done.error}

    return task


def check_aws(session_factory=boto3.Session) -> None:
    profile = os.environ.get("AWS_PROFILE", "sandbox")
    try:
        session_factory(profile_name=profile).client("sts").get_caller_identity()
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(f"AWS credentials expired or missing ({exc}). Run: aws sso login --profile {profile}") from exc


def _commit() -> str:
    return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", choices=["v1", "current"], default="v1")
    parser.add_argument("--data", choices=list(DATASETS), default="mock")
    parser.add_argument("--case", help="run a single case by id")
    args = parser.parse_args(argv)

    client = setup_tracing()
    if client is None:
        raise SystemExit("Langfuse is not configured: set LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY and "
                         "LANGFUSE_BASE_URL in .env (see .env.example)")
    directory = data_dir(args.data)
    cases = load_cases(directory)
    schemas = load_schemas(directory)
    upload_dataset(client, args.data, cases)

    metadata = {"version": args.version, "commit": _commit()}
    if args.version == "v1":
        check_aws()
        sync_seed(PROMPT_NAME, client)
        prompt = get_system_prompt(PROMPT_NAME, client)
        llm = create_llm()
        task = make_v1_task(llm, prompt.text, schemas)
        metadata |= {"model": llm.model, "prompt": f"{prompt.name}:v{prompt.version}"}
    else:
        task = current_task

    dataset = client.get_dataset(DATASETS[args.data])
    items = [i for i in dataset.items if not args.case or i.metadata.get("case") == args.case]
    if not items:
        raise SystemExit(f"No case {args.case} in {DATASETS[args.data]}")
    result = client.run_experiment(
        name=f"{args.version}-{args.data}", data=items, task=task,
        evaluators=[make_item_evaluator(schemas)], run_evaluators=[make_run_evaluator(schemas)],
        max_concurrency=MAX_CONCURRENCY, metadata=metadata)
    print(result.format())
    client.flush()


if __name__ == "__main__":
    main()
