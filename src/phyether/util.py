from typing import Iterable


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
