from typing import Union, cast, overload

from galois import Array, GF, Poly, ReedSolomon, lagrange_poly

import numpy as np
from numpy.linalg import LinAlgError

from phyether.util import iterable_to_string, string_to_bytes, string_to_list


class RS_Original:
    def __init__(self, codeword_length: int, message_length: int, field_order: int = 2**8):
        """_summary_

        :param codeword_length: Length of generated codeword in symbols
        :param message_length: Maximum length of message in symbols
        :param field_order: Order of galois field. Allowed symbol values: <0, field_order)
        """
        if not message_length < codeword_length < field_order:
            raise ValueError(f"Values must fulfill: {message_length} < {codeword_length} < {field_order}")
        self.codeword_length = codeword_length
        self.message_length = message_length
        self.gf = GF(field_order)
        self.parity_evaluation_points = [
            int(self.gf.primitive_element ** power)
            for power in range(self.message_length, self.codeword_length)
        ]
        self.parity_length = codeword_length - message_length
        self.max_errors = self.parity_length // 2
        self.dtype = self.gf(0).dtype
        self.primitive_powers = [self.gf.primitive_element**i for i in range(self.codeword_length)]
        self.rs = ReedSolomon(
            n=field_order - 1,
            k=field_order - self.parity_length - 1,
            field=self.gf)

    @overload
    def encode(self, message: str) -> str:
        ...

    @overload
    def encode(self, message: list[int]) -> list[int]:
        ...

    def encode(self, message: Union[str, list[int]]) -> Union[str, list[int]]:
        """encode message

        :param message: message to encode
        :return: return encoded message
        """
        # TODO: check message length
        list_message = string_to_list(message) if isinstance(message, str) else message
        if len(list_message) > self.message_length:
            raise ValueError(f"Message is {len(list_message)} symbols in size. "
                             f"Max is {self.message_length}")
        if len(list_message) == 0:
            raise ValueError("Message is empty! Can't encode nothing")
        if isinstance(message, str):
            return iterable_to_string(self.rs.encode(list_message))
        else:
            encoded_list: list[int] = self.rs.encode(list_message).tolist()
            return encoded_list

    @overload
    def decode(self, codeword: str) -> tuple[str, int]:
        ...

    @overload
    def decode(self, codeword: list[int]) -> tuple[list[int], int]:
        ...

    def decode(self, codeword: Union[str, list[int]]) -> tuple[Union[str, list[int]], int]:
        """decode codeword

        :param codeword: codeword to decode
        :return: decoded message
        """
        list_codeword = string_to_list(codeword) if isinstance(codeword, str) else codeword
        if len(codeword) > self.codeword_length:
            raise ValueError(f"Codeword is {len(codeword)} symbols in size. "
                             f"Max is {self.codeword_length}")
        if len(codeword) <= self.parity_length + 1:
            raise ValueError(f"Codeword can't be shorter than {self.parity_length + 1} = "
                             f"{self.parity_length} parity symbols + 1 message symbol")
        decoded, errors = self.rs.decode(list_codeword, errors=True)
        if isinstance(codeword, str):
            return iterable_to_string(decoded), int(errors)
        else:
            return decoded.tolist(), int(errors)

    @overload
    def encode_custom(self, message: str) -> str:
        ...

    @overload
    def encode_custom(self, message: list[int]) -> list[int]:
        ...

    def encode_custom(self, message: Union[str, list[int]]) -> Union[str, list[int]]:
        """Encodes message. Message is padded with '\\0' if it's shorter than self.message_length

        Args:
            message (str | list[int]): message to encode
        """
        if isinstance(message, str):
            message = list(string_to_bytes(message).ljust(self.message_length, b'\0'))
            return_string = True
        else:
            message.extend([0] * (self.message_length - len(message)))
            return_string = False
        if len(message) > self.message_length:
            raise ValueError(f"Message is {len(message)} symbols in size. "
                             f"Max is {self.message_length}")

        message_evaluation_points = [
            int(self.gf.primitive_element ** power)
            for power in range(self.message_length)
        ]
        evaluation_points = message_evaluation_points + self.parity_evaluation_points

        p_m = lagrange_poly(self.gf(message_evaluation_points), self.gf(message))
        encoded_message = p_m(evaluation_points)
        if return_string:
            return iterable_to_string(encoded_message)
        else:
            return cast(list[int], encoded_message.tolist())

    @overload
    def decode_custom(self, codeword: str) -> tuple[str, int]:
        ...

    @overload
    def decode_custom(self, codeword: list[int]) -> tuple[list[int], int]:
        ...

    def decode_custom(self, codeword: Union[str, list[int]]) -> tuple[Union[str, list[int]], int]:
        """Decode codeword using berlekamp-welch algorithm

        :param codeword: codeword to encode
        :raises ValueError: if len(codeword) != self.codeword_length
        :return: decoding_failed, decoded codeword
        """
        if isinstance(codeword, str):
            codeword = string_to_list(codeword)
            return_string = True
        else:
            return_string = False
        if len(codeword) != self.codeword_length:
            raise ValueError(f"Codeword is {len(codeword)} symbols in size, "
                             f"it should be {self.codeword_length} symbols")
        decoded, errors = self._berlekamp_welch(codeword)
        if return_string:
            return iterable_to_string(decoded), errors
        else:
            return decoded.tolist(), errors

    def _berlekamp_welch(self, codeword: list[int]) -> tuple[Array, int]:
        """Implementation of berlekamp-welch algorithm

        :param codeword:
        :return: decoded message, errors
        """
        for e in range(self.max_errors, -1, -1):
            A = []
            try:
                q = self.codeword_length - e - 1
                for code_symbol, primitive_power in zip(codeword, self.primitive_powers):
                    A.append([self.gf(code_symbol) * primitive_power**j for j in range(e)
                              ] + [-primitive_power**j for j in range(q + 1)])
                A_gf = self.gf(A)
                b = self.gf([-(self.gf(codeword[i]) * self.primitive_powers[i]**e)
                            for i in range(self.codeword_length)])  # type: ignore
                x = list(reversed(np.linalg.solve(A_gf, b)))
            except LinAlgError:
                continue
            break
        if e == 0:
            return self.gf(codeword[:self.message_length]), 0
        else:
            Q = Poly(x[:q + 1], self.gf)
            E = Poly([1] + x[q + 1:], self.gf)
            F, remainder = divmod(Q, E)
            message = codeword.copy()[:self.message_length]
            is_error = remainder != Poly.Zero(self.gf)
            if not is_error:
                errors = [i for i in range(self.message_length) if E(self.primitive_powers[i]) == 0]
                for error in errors:
                    message[error] = int(F(self.primitive_powers[error]))
            return self.gf(message), -1 if is_error else e
