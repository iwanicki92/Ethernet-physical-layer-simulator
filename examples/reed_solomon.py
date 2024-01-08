from typing import Literal, overload

import numpy as np

from phyether.reed_solomon import RS_Original
from phyether.util import iterable_to_string, string_to_list


def main():
    rs = RS_Original(192, 186)
    message = "abcdefghijklmn"
    encoded = rs.encode(message)
    corrupted_encoded = corrupt_message(encoded, 3, "beginning")
    decoded, errors = rs.decode(corrupted_encoded)
    print_encoding(message, encoded, corrupted_encoded, decoded, errors == -1)

    corrupted_encoded = corrupt_message(encoded, 4, "beginning")
    decoded, errors = rs.decode(corrupted_encoded)
    print_encoding(message, encoded, corrupted_encoded, decoded, errors == -1)


@overload
def print_encoding(message: str, encoded: str, corrupted_encoded: str,
                   decoded: str, errors: bool) -> None:
    ...


@overload
def print_encoding(message: str, encoded: list[int], corrupted_encoded: list[int],
                   decoded: list[int], errors: bool) -> None:
    ...


def print_encoding(message, encoded, corrupted_encoded, decoded, errors):
    if isinstance(encoded, list):
        encoded = iterable_to_string(encoded)
        corrupted_encoded = iterable_to_string(corrupted_encoded)
        decoded = iterable_to_string(decoded)
    if errors:
        print("Message couldn't be decoded correctly!")
    else:
        print('Message decoded successfully')
    print(f'Original message: {message}')
    print(f'Encoded message: {encoded}')
    print(f'Corrupted message: {corrupted_encoded}')
    print(f'Decoded message: {decoded}')
    print('')


@overload
def corrupt_message(
    message: str, number_of_errors: int,
        corruption_type: Literal['beginning', 'ending', 'random'] = "random") -> str:
    ...


@overload
def corrupt_message(
    message: list[int], number_of_errors: int,
        corruption_type: Literal['beginning', 'ending', 'random'] = "random") -> list[int]:
    ...


def corrupt_message(message, number_of_errors, corruption_type="random"):
    if isinstance(message, str):
        message = string_to_list(message)
        return_string = True
    else:
        return_string = False
    assert number_of_errors <= len(message)
    errors = np.random.choice(255, size=number_of_errors, replace=False).tolist()
    if corruption_type == "beginning":
        message[:number_of_errors] = errors
    elif corruption_type == "ending":
        message[-number_of_errors:] = errors
    else:
        random_errors = np.random.choice(len(message), size=number_of_errors, replace=False)
        for error_index in random_errors:
            message[error_index] = np.random.randint(0, 255)
    if return_string:
        return iterable_to_string(message)
    else:
        return message


if __name__ == "__main__":
    main()
