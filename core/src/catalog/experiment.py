"""Run a version of the catalog agent as a Langfuse experiment.

    scripts/experiment.sh --version v1 --data mock
    scripts/experiment.sh --version current --data mock      # today's process, no model
    scripts/experiment.sh --version v1 --data mock --case error-88904447

`--data real` uploads the 30 real Alephee/GM products to Langfuse Cloud: it needs
`--allow-real-upload`, which waits for Alephee's confirmation (see CLAUDE.md).
"""

import argparse
import os
import subprocess

import boto3

from .data import data_dir, load_cases, load_schemas
from .evaluation import make_item_evaluator, make_run_evaluator
from .llm import auth_error_message, create_llm, is_auth_error
from .prompts import PROMPT_NAME, get_system_prompt, sync_seed
from .tracing import setup_tracing
from .v1 import MappingV1

DATASETS = {"real": "alephee-shopee-real", "mock": "alephee-shopee-mock"}
MAX_CONCURRENCY = 4
REAL_DATA_WARNING = (
    "Uploading the 30 real Alephee/GM products to Langfuse Cloud waits for Alephee's "
    "confirmation. Pass --allow-real-upload once Alephee confirms."
)


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
        try:
            done = await workflow_cls(llm=llm, system_prompt=system_prompt, schemas=schemas, timeout=180).run(
                product=item.input)
        except Exception as exc:  # noqa: BLE001 — only an auth error is special-cased, see below
            cause = exc.__cause__
            if is_auth_error(exc) or (cause is not None and is_auth_error(cause)):
                # An SSO token that expires mid-run would otherwise fail every remaining
                # item one by one; stopping the whole experiment here is cheaper to notice.
                raise SystemExit(auth_error_message(exc, os.environ.get("AWS_PROFILE") or None)) from exc
            raise
        return done.listing.model_dump() if done.listing is not None else {"error": done.error}

    return task


def check_aws(session_factory=boto3.Session) -> None:
    # Same source as `create_llm`: a profile set in the env, or `None` for the default chain.
    profile = os.environ.get("AWS_PROFILE") or None
    try:
        session_factory(profile_name=profile).client("sts").get_caller_identity()
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(auth_error_message(exc, profile)) from exc


def prompt_label(prompt) -> str:
    """Run metadata label: the seed has no version, a Langfuse prompt has one."""
    return f"{prompt.name}:seed" if prompt.version is None else f"{prompt.name}:v{prompt.version}"


def _commit() -> str:
    return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", choices=["v1", "current"], default="v1")
    parser.add_argument("--data", choices=list(DATASETS), default="mock")
    parser.add_argument("--case", help="run a single case by id")
    parser.add_argument("--allow-real-upload", action="store_true",
                        help="confirm uploading the 30 real Alephee/GM products to Langfuse Cloud")
    args = parser.parse_args(argv)

    if args.data == "real" and not args.allow_real_upload:
        raise SystemExit(REAL_DATA_WARNING)

    client = setup_tracing()
    if client is None:
        raise SystemExit("Langfuse is not configured: set LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY and "
                         "LANGFUSE_BASE_URL in .env (see .env.example)")
    directory = data_dir(args.data)
    cases = load_cases(directory)
    schemas = load_schemas(directory)

    metadata = {"version": args.version, "commit": _commit()}
    if args.version == "v1":
        # Before uploading anything: an expired SSO session should stop the run here,
        # not after the dataset is already up and the first model call fails.
        check_aws()
    upload_dataset(client, args.data, cases)
    if args.version == "v1":
        sync_seed(PROMPT_NAME, client)
        prompt = get_system_prompt(PROMPT_NAME, client)
        llm = create_llm()
        task = make_v1_task(llm, prompt.text, schemas)
        metadata |= {"model": llm.model, "prompt": prompt_label(prompt)}
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
