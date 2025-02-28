import argparse

from src.build.nodes import build_nodes
from src.build.signals import build_signals


def get_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="eVED database builder")
    parser.add_argument(
        "--signals",
        dest="signals",
        action="store_true",
        default=False,
        help="build base signals table",
    )
    parser.add_argument(
        "--nodes",
        dest="nodes",
        action="store_true",
        default=False,
        help="build base nodes table",
    )
    return parser


def main():
    parser = get_argument_parser()
    args = parser.parse_args()

    if args.signals:
        build_signals()

    if args.nodes:
        build_nodes()


if __name__ == "__main__":
    main()
