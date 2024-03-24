import logging
import argparse
import dfs

_logger = logging.getLogger(__name__)


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

    parser_scan = subparsers.add_parser("ignore")
    ignore_sub = parser_scan.add_subparsers(dest="subcommand")
    # list
    parser_scan_list = ignore_sub.add_parser("list")
    parser_scan_list.add_argument("db", help="path to file with database")
    # add
    parser_scan_add = ignore_sub.add_parser("add")
    parser_scan_add.add_argument("db", help="path to file with database")
    parser_scan_add.add_argument("path", help="path to the files to be ignored")
    # remove
    parser_scan_remove = ignore_sub.add_parser("remove")
    parser_scan_remove.add_argument("db", help="path to file with database")
    parser_scan_remove.add_argument("path", help="path to be removed from ignore list")

    args = parser.parse_args()
    if args.command == "init":
        db_file = args.db
        path = args.path
        dfs.init(db_file, path)
    elif args.command == "scan":
        db_file = args.db
        path = args.path
        fast = args.fast
        dfs.scan(db_file, path, fast=fast)
    elif args.command == "ignore":
        db_file = args.db
        if args.subcommand == "list":
            dfs.ignore_list(db_file)
        elif args.subcommand == "add":
            path = args.path
            dfs.ignore_add(db_file, path)
        elif args.subcommand == "remove":
            path = args.path
            dfs.ignore_remove(db_file, path)
        else:
            _logger.error(f"Unknown subcommand: ignore {args.subcommand}")
            exit(1)
    else:
        _logger.error(f"Unknown command: {args.command}")
        exit(1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
