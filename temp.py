import logging
import pathlib

_logger = logging.getLogger(__name__)


def main():
    p = pathlib.Path("c:\\usr\\bin\\a.txt")
    _logger.info(f"{isinstance(p, pathlib.PurePosixPath)}")
    _logger.info(f"{isinstance(p, pathlib.PureWindowsPath)}")
    par = pathlib.Path('c:\\')
    _logger.info(f"{p.relative_to(par).as_posix()}")
    _logger.info(f"{p}")
    _logger.info(f"{p.is_absolute()}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
