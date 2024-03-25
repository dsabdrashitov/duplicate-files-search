import logging
import csv
from typing import Set, Iterable

_logger = logging.getLogger(__name__)


def load_files_collection(filename: str) -> Set[str]:
    result = set()
    with open(filename, newline="", encoding="utf-8") as csv_file:
        for row in csv.reader(csv_file):
            assert len(row) == 1
            result.add(row[0])
    return result


def save_files_collection(filename: str, files: Iterable[str]) -> None:
    with open(filename, "w", newline="", encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file)
        for name in files:
            csv_writer.writerow([name])
