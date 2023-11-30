from typing import Iterable, Literal, List
from collections.abc import Mapping

def list_from_string(string: str, base: int = 10):
    """convert str: "0 2 34 20..." to List[int]: [0, 2, 34, 20...]

    :param string: string to convert
    :param base: what base are numbers in string
    """
    return [int(x, base) for x in string.split()]

def list_to_string(list_to_convert: List[int], base: Literal[2, 10, 16] = 10):
    """convert List[int]: [1,2,3,...] to string: "1 2 3 ..."

    :param list_to_convert: list with integers to convert
    """
    if base == 2:
        int_to_base = lambda x: f'{x:08b}'
    elif base == 10:
        int_to_base = lambda x: f'{x}'
    else:
        int_to_base = lambda x: f'{x:02x}'

    return ' '.join(int_to_base(x) for x in list_to_convert)

def iterable_to_string(iterable: Iterable[int]) -> str:
    """Decodes iterable as string. Each element is treated as utf-8 byte
    """
    return bytes(iterable).decode(errors="surrogateescape")


def string_to_bytes(string: str) -> bytes:
    """Encodes string as utf-8 bytes
    """
    return string.encode(errors="surrogateescape")


def string_to_list(string: str) -> List[int]:
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
