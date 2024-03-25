import logging
from pathlib import Path
import os
import hashlib
from typing import List, Dict, Set
from .hashes_file import load_hashes, save_hashes, FileHash
from .files_file import load_files_collection

_logger = logging.getLogger(__name__)

_BUFFER_SIZE = 65536
_PROGRESS_DOTS = 25


def _process_file(file_path: Path, file_hash: FileHash, fast: bool, existing: Dict[str, FileHash]) -> None:
    print('[', end='', flush=True)
    if fast and (file_hash.path in existing) and (existing[file_hash.path].size == file_hash.size):
        file_hash.hash_hex = existing[file_hash.path].hash_hex
        print('c' * _PROGRESS_DOTS, end='')
    else:
        h = hashlib.md5()
        with file_path.open("rb") as f:
            done = 0
            done_p = 0
            while True:
                buf = f.read(min(file_hash.size, _BUFFER_SIZE))
                if not buf:
                    break
                h.update(buf)
                done = done + len(buf)
                need_p = done * _PROGRESS_DOTS // file_hash.size
                if done_p < need_p:
                    print('.' * (need_p - done_p), end='', flush=True)
                    done_p = need_p
        file_hash.hash_hex = h.hexdigest()
    print(']')


def _traverse(p: Path, ignore: Set[str], result: List[Path], visited: Set[str]) -> None:
    if str(p) in ignore:
        _logger.info(f"Ignored: {p}")
        return
    _logger.info(f"Traversing: {p}")
    if p.is_file():
        result.append(p)
    elif p.is_dir():
        visited.add(str(p))
        empty = True
        for child in p.iterdir():
            _traverse(child, ignore, result, visited)
            empty = False
        if empty:
            result.append(p)
    else:
        _logger.warning(f"Unknown path type: {p}")


def _normal(path: str) -> str:
    return str(Path(path).absolute())


def scan(hashes_file: str, path: str, ignore_file: str = None, fast: bool = False):
    ignore = set()
    if ignore_file is not None:
        _logger.info(f"Loading ignore set from: {ignore_file}")
        for i in load_files_collection(ignore_file):
            ni = _normal(i)
            ignore.add(ni)
            _logger.info(f"Ignore: {ni}")

    _logger.info(f"Loading hashes from: {hashes_file}")
    hashes = load_hashes(hashes_file)
    existing: Dict[str, FileHash] = {}
    for h in hashes:
        existing[_normal(h.path)] = h

    _logger.info(f"Collecting files from: {path}")
    scanned_paths: List[Path] = []
    visited: Set[str] = set()
    _traverse(Path(path).absolute(), ignore, scanned_paths, visited)

    _logger.info(f"Calculating sizes.")
    scanned: Dict[str, FileHash] = {}
    size_sum = 0
    for i in range(len(scanned_paths)):
        p = scanned_paths[i]
        ps = str(p)
        if p.is_file():
            size = os.path.getsize(p)
            size_sum = size_sum + size
            scanned[ps] = FileHash(ps, size, None)
        else:
            scanned[ps] = FileHash(ps, None, None)
        _logger.info(f"({(i * 100 / len(scanned_paths)):.2f}%) {ps}")

    _logger.info(f"Calculating hashes.")
    size_done = 0
    for i in range(len(scanned_paths)):
        p = scanned_paths[i]
        ps = str(p)
        _logger.info(f"({(i * 100 / len(scanned_paths)):.2f}%, {(size_done * 100 / size_sum):.2f}%) {ps}")
        if p.is_file():
            ph = scanned[ps]
            _process_file(p, ph, fast, existing)
            size_done = size_done + ph.size

    _logger.info(f"Merging with existing.")
    to_kill = []
    for ps, ph in existing.items():
        if str(Path(ps).parent) in visited:
            to_kill.append(ps)
    for ps in to_kill:
        del existing[ps]
    _logger.info(f"Killed: {len(to_kill)}")
    for ps, ph in scanned.items():
        existing[ps] = ph
    _logger.info(f"Added: {len(scanned)}")

    hashes = [ph for ph in existing.values()]
    save_hashes(hashes_file, hashes)
    _logger.info(f"Scan {path} to {hashes_file} done.")
