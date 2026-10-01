"""Load a correction from the catalog team and drop the cached mappings of that category.

    scripts/correct.sh --category <urn> --attribute <urn> --product-value <value> --value-id <id> --value <name>
"""

import argparse
from datetime import date

from .data import data_dir, load_schemas
from .store import Correction, stores_from_env


def _check(category: str, attribute: str, value_id: str, value: str) -> None:
    schemas = {**load_schemas(data_dir("mock")), **load_schemas(data_dir("real"))}
    definition = next((a for a in schemas.get(category, {}).get("attributes", []) if a["urn"] == attribute), None)
    if definition is None:
        raise SystemExit(f"{attribute} is not an attribute of {category}")
    domain = {str(v["id"]): v["name"] for v in definition.get("values") or []}
    # Free-text attributes have no `values` list: accepted without a domain check on purpose.
    if domain and domain.get(value_id) != value:
        raise SystemExit(f"{value} (id {value_id}) is not in the channel list of {attribute}")


def main(argv: list[str] | None = None, stores=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for flag in ("--category", "--attribute", "--product-value", "--value-id", "--value"):
        parser.add_argument(flag, required=True)
    parser.add_argument("--author", default="catalog")
    args = parser.parse_args(argv)
    _check(args.category, args.attribute, args.value_id, args.value)
    corrections, cache, label = stores or stores_from_env()
    corrections.put(Correction(category_urn=args.category, attribute_urn=args.attribute, product_value=args.product_value,
                               value_id=args.value_id, value=args.value, author=args.author,
                               created_at=date.today().isoformat()))
    dropped = cache.invalidate_category(args.category)
    print(f"Correction stored ({label}); {dropped} cached mappings of {args.category} dropped.")


if __name__ == "__main__":
    main()
