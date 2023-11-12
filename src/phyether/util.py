from typing import Iterable
from collections.abc import Mapping

def list_from_string(string):
    """convert str: "0 2 34 20..." to list[int]: [0, 2, 34, 20...]

    :param string: string to convert
    """
    return [int(x) for x in string.split()]

def list_to_string(list_to_convert):
    """convert list[int]: [1,2,3,...] to string: "1 2 3 ..."
    """
    return ' '.join(str(x) for x in list_to_convert)

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
