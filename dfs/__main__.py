import logging
import argparse
import dfs

_logger = logging.getLogger(__name__)


def _init(args):
    db_file = args.db
    path = args.path
    dfs.init(db_file, path)


def _scan(args):
    db_file = args.db
    path = args.path
    fast = args.fast
    dfs.scan(db_file, path, fast=fast)


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    parser_init = subparsers.add_parser("init")
    parser_init.add_argument("db", help="path to file with database")
    parser_init.add_argument("path", help="base path of files being scanned")

    parser_scan = subparsers.add_parser("scan")
    parser_scan.add_argument("db", help="path to file with database")
    parser_scan.add_argument("path", help="path to the files to be scanned")
    parser_scan.add_argument("-f", "--fast", action='store_true', help="option for skip hash calculation for known "
                                                                       "files")

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
