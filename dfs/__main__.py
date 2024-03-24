import logging
import argparse
import dfs

_logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    parser_init = subparsers.add_parser("init", help="init file with hashes collection")
    parser_init.add_argument("hashes", help="path to file with hashes")

    parser_scan = subparsers.add_parser("scan", help="scan path and add it's subtree to hashes collection")
    parser_scan.add_argument("hashes", help="path to file with hashes (will be overwritten)")
    parser_scan.add_argument("path", help="path to the files to be scanned")
    parser_scan.add_argument("-i", "--ignore", help="")
    parser_scan.add_argument("-f", "--fast", action='store_true', help="option for skip hash calculation for known "
                                                                       "files")

    parser_files = subparsers.add_parser("files", help="manipulations with lists of files")
    files_sub = parser_files.add_subparsers(dest="subcommand")
    # init
    parser_files_init = files_sub.add_parser("init", help="create empty")
    parser_files_init.add_argument("list", help="path to file with list")
    # add file
    parser_files_add = files_sub.add_parser("add")
    parser_files_add.add_argument("list", help="path to file with list")
    parser_files_add.add_argument("path", help="path to be added")
    # remove file
    parser_files_remove = files_sub.add_parser("remove")
    parser_files_remove.add_argument("list", help="path to file with list")
    parser_files_remove.add_argument("path", help="path to be removed")

    args = parser.parse_args()
    if args.command == "init":
        hashes_file = args.db
        dfs.save_hashes(hashes_file, [])
    elif args.command == "scan":
        pass
        # db_file = args.db
        # path = args.path
        # fast = args.fast
        # dfs.scan(db_file, path, fast=fast)
    elif args.command == "files":
        files_file = args.list
        if args.subcommand == "init":
            dfs.save_files_collection(files_file, [])
        elif args.subcommand == "add":
            path = args.path
            files_set = dfs.load_files_collection(files_file)
            files_set.add(path)
            dfs.save_files_collection(files_file, files_set)
        elif args.subcommand == "remove":
            path = args.path
            files_set = dfs.load_files_collection(files_file)
            files_set.remove(path)
            dfs.save_files_collection(files_file, files_set)
        else:
            _logger.error(f"Unknown subcommand: files {args.subcommand}")
            exit(1)
    else:
        _logger.error(f"Unknown command: {args.command}")
        exit(1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
