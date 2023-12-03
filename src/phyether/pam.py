from abc import ABC, abstractmethod
from bitarray import bitarray

from phyether.util import removeprefix

class PAM(ABC):
    @property
    def symbol_step(self):
        return 2

    @property
    @abstractmethod
    def high_symbol(self) -> int:
        pass

    @abstractmethod
    def hex_to_signals(self, hex_data: str) -> str:
        pass


class NRZ(PAM):
    @property
    def high_symbol(self):
        return 1

    def hex_to_signals(self, hex_data: str) -> str:
        return ' '.join([
            '1' if bit == '1' else '-1'
            for bit in format(int(hex_data, 16), 'b')
            ])

class PAM4(PAM):
    @property
    def high_symbol(self):
        return 3

    def hex_to_signals(self, hex_data: str) -> str:
        binary = format(int(hex_data, 16), 'b')
        if len(binary) % 2 == 1:
            binary.rjust(len(binary) + 1, '0')
        return ' '.join(
            str(-3 + 2*int(binary[bit:bit+2], 2))
            for bit in range(0, len(binary), 2))

class PAM16(PAM):
    @property
    def high_symbol(self) -> int:
        return 15

    def hex_to_signals(self, hex_data: str, use_dsq128: bool = False):
        if use_dsq128:
            return PAM16._hex_to_signals_dsq128(hex_data)
        else:
            return ' '.join(
                str(-15 + 2*int(hex_symbol,16))
                for hex_symbol in removeprefix(hex_data, "0x"))

    @staticmethod
    def _bits_to_dsq128(bits: bitarray) -> tuple[int, int]:
            """
            converts 7-bit frame into 2D DSQ128 symbol
            """

            assert(len(bits) == 7)
            u = bits[0:3]
            c = bits[3:]

            # Step 1
            x13 = -u[0] & u[2]
            x12 = u[0] ^ u[2]
            x11 = c[0]
            x10 = c[0] ^ c[1]
            x23 = (u[1] & u[2]) + (u[0] & -u[1])
            x22 = u[1] ^ u[2]
            x21 = c[2]
            x20 = c[2] ^ c[3]

            # Step 2
            x1 = 8*x13 + 4*x12 + 2*x11 + x10
            x2 = 8*x23 + 4*x22 + 2*x21 + x20

            # Step 3
            y1 = (x1 + x2) % 16
            y2 = (-x1 + x2) % 16

            # Step 4
            return 2*y1 - 15, 2*y2 - 15

    @staticmethod
    def _hex_to_signals_dsq128(hex_data: str):
        bits = bitarray(bin(int(hex_data, 16))[2:])
        padding_length = (28 - (len(bits) % 28)) % 28
        bits += bitarray('0' * padding_length)
        twisted_pairs_output = ["", "", "", ""]

        for i in range(0, len(bits), 28):
            group = bits[i:i+28]
            for idx in range(len(twisted_pairs_output)):
                group_idx = idx*7
                pam16_1, pam16_2 = PAM16._bits_to_dsq128(group[group_idx:group_idx+7])
                twisted_pairs_output[idx] += " " + str(pam16_1) + " " + str(pam16_2)

        return [output[1:] for output in twisted_pairs_output]
