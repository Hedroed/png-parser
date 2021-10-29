from enum import Enum


class Color(Enum):
    r = '\033[0m'
    line = '\033[93m'
    chunk = '\033[34m'
    length = '\033[36m'
    data = '\033[0m'
    crc = '\033[35m'
    text = '\033[92m'
    id = '\033[33m'
    unknown = '\033[31m'

    def __str__(self):
        return str(self.value)
