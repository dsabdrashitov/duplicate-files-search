import logging
import argparse
import dfs

_logger = logging.getLogger(__name__)


def _init(args):
    db_file = args.db
    dfs.init(db_file)


def _scan(args):
    db_file = args.db
    path = args.path
    dfs.scan(db_file, path)


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    parser_init = subparsers.add_parser("init")
    parser_init.add_argument("db", help="path to file with database")

    parser_scan = subparsers.add_parser("scan")
    parser_scan.add_argument("db", help="path to file with database")
    parser_scan.add_argument("path")

    args = parser.parse_args()
    if args.command == "init":
        _init(args)
    elif args.command == "scan":
        _scan(args)
    else:
        _logger.error(f"Unknown command: {args.command}")
        exit(1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
