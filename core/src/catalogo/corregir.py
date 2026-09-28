"""Carga una corrección del equipo de catálogo en la memoria de la V3.

    scripts/corregir.sh --categoria urn:category:102529:vendor:shopee \\
        --urn urn:attribute:101730:vendor:shopee --valor-producto Centro --value-id 14729 --value Parcial
"""

import argparse
import json

from .memoria import Memoria


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for arg in ("--categoria", "--urn", "--valor-producto", "--value-id", "--value"):
        parser.add_argument(arg, required=True)
    parser.add_argument("--autor", default="catálogo")
    args = parser.parse_args()
    correccion = Memoria().corregir(args.categoria, args.urn, args.valor_producto, args.value_id, args.value, args.autor)
    print(json.dumps(correccion, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
