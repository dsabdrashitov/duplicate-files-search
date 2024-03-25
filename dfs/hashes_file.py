import logging
import csv
from typing import List, Optional

_logger = logging.getLogger(__name__)


class FileHash:

    def __init__(self, path: str, size: Optional[int], hash_hex: Optional[str]):
        """
        :param path:
        :param size: None for empty directory
        :param hash_hex: None for empty directory
        """
        self.path = path
        self.size = size
        self.hash_hex = hash_hex


def load_hashes(filename: str) -> List[FileHash]:
    result = []
    with open(filename, newline="", encoding="utf-8") as csv_file:
        for row in csv.reader(csv_file):
            if row[1] == '':
                result.append(FileHash(row[0], None, None))
            else:
                result.append(FileHash(row[0], int(row[1]), row[2]))
    return result


def save_hashes(filename: str, hashes_list: List[FileHash]) -> None:
    with open(filename, "w", newline="", encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file)
        for row in hashes_list:
            csv_writer.writerow([row.path, row.size, row.hash_hex])
