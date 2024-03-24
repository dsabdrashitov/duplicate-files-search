import logging
import pathlib
from dfs.hashes_file import load_hashes, save_hashes, FileHash

_logger = logging.getLogger(__name__)


def main():
    p = pathlib.Path("c:\\usr\\bin\\a.txt")
    _logger.info(f"{isinstance(p, pathlib.PurePosixPath)}")
    _logger.info(f"{isinstance(p, pathlib.PureWindowsPath)}")
    par = pathlib.Path('c:\\')
    _logger.info(f"{p.relative_to(par).as_posix()}")
    _logger.info(f"{p}")
    _logger.info(f"{p.is_absolute()}")
    root = pathlib.Path('/aba/../aba')
    _logger.info(f"{root}")
    _logger.info(f"{root.parent.parent}")
    _logger.info(f"{root.parent.parent.parent}")
    save_hashes("data/a.csv", [
        FileHash("somefilewith,.-'\"quotes", 10, "abacaba"),
        FileHash("some\\filewith,.-'\"quotes", 13, "abac\"aba"),
        FileHash("somedir", None, None),
        FileHash("some/filewith,.-'\"quotes", 0, "abac'aba"),
    ])
    hashes = load_hashes("data/a.csv")
    _logger.info(f"{hashes}")
    save_hashes("data/b.csv", hashes)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
