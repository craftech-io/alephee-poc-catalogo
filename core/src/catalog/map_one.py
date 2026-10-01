"""Map one SKU and print the listing JSON exactly as the agent delivers it (urn, valueId, value, unit).

    scripts/map.sh 94701411                       # V2 on the mock dataset
    scripts/map.sh 94701411 --version v1
    scripts/map.sh 98550735 --data real

The chat tool turns urns into names for a readable table; this prints the raw contract instead.
It uses the prompt seed from the repo and in-memory corrections and cache, so it neither reads nor
writes DynamoDB and sends nothing to Langfuse. `source` goes to stderr so stdout stays valid JSON.
"""

import argparse
import asyncio
import sys

from .data import data_dir, find_product, load_schemas
from .llm import auth_error_message, create_llm, is_auth_error
from .prompts import PROMPT_NAME, PROMPT_NAME_V2, load_seed
from .reference import load_reference
from .store import InMemoryCache, InMemoryCorrections
from .v1 import MappingV1
from .v2 import MappingV2


def build(version: str, directory, llm):
    schemas = load_schemas(directory)
    if version == "v1":
        return MappingV1(llm=llm, system_prompt=load_seed(PROMPT_NAME), schemas=schemas, timeout=180)
    return MappingV2(llm=llm, system_prompt=load_seed(PROMPT_NAME_V2), prompt_version="seed", schemas=schemas,
                     reference=load_reference(directory), corrections=InMemoryCorrections(),
                     cache=InMemoryCache(), timeout=300)


async def run(sku: str, version: str, origin: str) -> int:
    directory = data_dir(origin)
    found = find_product(sku, [directory])
    if found is None:
        print(f"SKU {sku} is not in the {origin} dataset", file=sys.stderr)
        return 1
    product, _ = found
    try:
        done = await build(version, directory, create_llm()).run(product=product)
    except Exception as exc:  # noqa: BLE001
        if is_auth_error(exc) or is_auth_error(exc.__cause__ or exc):
            print(auth_error_message(exc, None), file=sys.stderr)
            return 1
        raise
    print(f"source: {done.source}" + (f" · error: {done.error}" if done.error else ""), file=sys.stderr)
    if done.listing is None:
        return 1
    print(done.listing.model_dump_json(indent=2))
    return 0


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("sku")
    parser.add_argument("--version", choices=["v1", "v2"], default="v2")
    parser.add_argument("--data", choices=["mock", "real"], default="mock")
    args = parser.parse_args(argv)
    raise SystemExit(asyncio.run(run(args.sku, args.version, args.data)))


if __name__ == "__main__":
    main()
