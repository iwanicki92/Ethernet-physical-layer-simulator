from typing import Union, cast, overload, Tuple, List

from galois import Array, GF, FieldArray, Poly, ReedSolomon, lagrange_poly

import numpy as np
from numpy.linalg import LinAlgError

from phyether.util import iterable_to_string, string_to_bytes, string_to_list


class RS_Original:
    def __init__(self, codeword_length: int, message_length: int, field_order: int = 2**8,
                 systematic: bool = True):
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
            field=self.gf, systematic=systematic)

    @overload
    def expand_message(self, message: str, size: int) -> Tuple[int, str]:
        ...

    @overload
    def expand_message(self, message: List[int], size: int) -> Tuple[int, List[int]]:
        ...

    def expand_message(self, message: Union[str, List[int]],
                       size: int) -> Tuple[int, Union[str, List[int]]]:
        if isinstance(message, str):
            message_bytes = string_to_bytes(message)
            original_size = len(message_bytes)
            message = list(message_bytes.rjust(size, b'\xff'))
            return original_size, iterable_to_string(message)
        else:
            original_size = len(message)
            message = ([255] * (size - len(message))) + message
            return original_size, message

    def shorten_codeword(self, codeword: Union[str, List[int]],
                         original_message_size: int) -> Union[str, List[int]]:

        return codeword[-(original_message_size + self.parity_length):]


    @overload
    def encode(self, message: str, custom: bool = False) -> str:
        ...

    @overload
    def encode(self, message: List[int], custom: bool = False) -> List[int]:
        ...

    def encode(self, message: Union[str, List[int]], custom: bool = False) -> Union[str, List[int]]:
        """encode message

        :param message: message to encode
        :param custom: use custom, slow, non BCH berlekamp-welch algorithm
        :return: return encoded message
        """
        if custom:
            return self.encode_custom(message)
        message_size = len(message)
        max_length = self.message_length
        if not self.rs.is_systematic:
            message_size, message = self.expand_message(message, self.rs.k)
            max_length = self.rs.k
        list_message = string_to_list(message) if isinstance(message, str) else message
        if len(list_message) > max_length:
            raise ValueError(f"Message is {len(list_message)} symbols in size. "
                             f"Max is {self.message_length}")
        if len(list_message) == 0:
            raise ValueError("Message is empty! Can't encode nothing")
        if isinstance(message, str):
            codeword: Union[str, List[int]] = iterable_to_string(self.rs.encode(list_message))
        else:
            codeword = self.rs.encode(list_message).tolist()
        return codeword

    @overload
    def decode(self, codeword: str, custom: bool = False,
               force: bool = False) -> Tuple[str, int, bool]:
        ...

    @overload
    def decode(self, codeword: List[int], custom: bool = False,
               force: bool = False) -> Tuple[List[int], int, bool]:
        ...

    def decode(self, codeword: Union[str, List[int]], custom: bool = False,
               force: bool = False) -> Tuple[Union[str, List[int]], int, bool]:
        """decode codeword

        :param codeword: codeword to decode
        :param custom: use custom, slow, non BCH berlekamp-welch algorithm
        :param force: try to force error fixing if custom is True
        :return: (decoded message, found errors, if those errors were fixed)
        """
        if custom:
            return self.decode_custom(codeword, force)
        codeword_size = len(codeword)
        list_codeword = string_to_list(codeword) if isinstance(codeword, str) else codeword
        max_length = self.codeword_length
        if not self.rs.is_systematic:
            codeword_size, list_codeword = self.expand_message(list_codeword, self.rs.n)
            max_length = self.rs.n
        if len(codeword) > max_length:
            raise ValueError(f"Codeword is {len(codeword)} symbols in size. "
                             f"Max is {self.codeword_length}")
        if len(codeword) <= self.parity_length:
            raise ValueError(f"Codeword can't be shorter than {self.parity_length + 1} = "
                             f"{self.parity_length} parity symbols + 1 message symbol")
        decoded: Union[str, List[int], FieldArray]
        decoded, fixed = self.rs.decode(list_codeword, errors=True)
        if isinstance(codeword, str):
            decoded = iterable_to_string(decoded)
        else:
            decoded = decoded.tolist()
        return decoded, int(fixed), True if fixed != -1 else False # type: ignore

    @overload
    def encode_custom(self, message: str) -> str:
        ...

    @overload
    def encode_custom(self, message: List[int]) -> List[int]:
        ...

    def encode_custom(self, message: Union[str, List[int]]) -> Union[str, List[int]]:
        """Encodes message. Message is padded with '\\0' if it's shorter than self.message_length

        :param message: message to encode
        """
        original_size: int
        if isinstance(message, str):
            message_bytes = string_to_bytes(message)
            original_size = len(message_bytes)
            message = list(message_bytes.ljust(self.message_length, b'\0'))
            return_string = True
        else:
            original_size = len(message)
            message.extend([0] * (self.message_length - len(message)))
            return_string = False
        if len(message) > self.message_length:
            raise ValueError(f"Message is {len(message)} symbols in size. "
                             f"Max is {self.message_length}")

        message_evaluation_points = [
            int(self.gf.primitive_element ** power)
            for power in range(self.message_length)
        ]

        p_m = lagrange_poly(self.gf(message_evaluation_points), self.gf(message))
        encoded_message = p_m(message_evaluation_points[:original_size])
        parity_message = p_m(self.parity_evaluation_points)
        if return_string:
            return iterable_to_string(encoded_message) + iterable_to_string(parity_message)
        else:
            return cast(List[int], encoded_message.tolist() + parity_message.tolist())

    @overload
    def decode_custom(self, codeword: str, force: bool = False) -> Tuple[str, int, bool]:
        ...

    @overload
    def decode_custom(self, codeword: List[int],
                      force: bool = False) -> Tuple[List[int], int, bool]:
        ...

    def decode_custom(self, codeword: Union[str, List[int]],
                      force: bool = False) -> Tuple[
            Union[str, List[int]], int, bool]:
        """Decode codeword using berlekamp-welch algorithm

        :param codeword: codeword to encode
        :param force: try to fix errors
        :raises ValueError: if len(codeword) != self.codeword_length
        :return: decoding_failed, decoded codeword
        """
        original_size = len(codeword)
        if isinstance(codeword, str):
            codeword = string_to_list(codeword)
            return_string = True
        else:
            return_string = False

        if len(codeword) > self.codeword_length:
            raise ValueError(f"Codeword is {len(codeword)} symbols in size, "
                             f"it should be {self.codeword_length} symbols")
        else:
            # extend codeword to correct length
            codeword[-self.parity_length:1] = [0]*(self.codeword_length - len(codeword))
        decoded, errors, fixed = self._berlekamp_welch(codeword, force)
        decoded = decoded.tolist()[:original_size - self.parity_length]
        if return_string:
            return iterable_to_string(decoded), errors, fixed
        else:
            return decoded, errors, fixed # type: ignore

    def _berlekamp_welch(self, codeword: List[int], force: bool = False) -> Tuple[Array, int, bool]:
        """Implementation of berlekamp-welch algorithm

        :param codeword:
        :param force: fix errors even if polynomial division remainder wasn't 0
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
            return self.gf(codeword[:self.message_length]), 0, True
        else:
            Q = Poly(x[:q + 1], self.gf)
            E = Poly([1] + x[q + 1:], self.gf)
            F, remainder = divmod(Q, E)
            message = codeword.copy()[:self.message_length]
            is_error = remainder != Poly.Zero(self.gf)
            num_errors = -1 if is_error else e
            if not is_error or force:
                errors = [i for i in range(self.message_length) if E(self.primitive_powers[i]) == 0]
                num_errors = len(errors)
                for error in errors:
                    message[error] = int(F(self.primitive_powers[error]))
            return self.gf(message), num_errors, not is_error
