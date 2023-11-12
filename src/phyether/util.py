from typing import Iterable
from collections.abc import Mapping


def iterable_to_string(iterable: Iterable[int]) -> str:
    """Decodes iterable as string. Each element is treated as utf-8 byte
    """
    return bytes(iterable).decode(errors="surrogateescape")


def string_to_bytes(string: str) -> bytes:
    """Encodes string as utf-8 bytes
    """
    return string.encode(errors="surrogateescape")


def string_to_list(string: str) -> list[int]:
    """Encodes string as utf-8 bytes
    """
    return list(string.encode(errors="surrogateescape"))

class DictMapping(Mapping):
    def __getitem__(self, key):
        return self.__dict__[key]

    def __iter__(self):
        return iter(self.__dict__.keys())

    def __len__(self):
        return len(self.__dict__)
