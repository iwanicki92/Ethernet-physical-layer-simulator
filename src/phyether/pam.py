from abc import ABC, abstractmethod

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

    def hex_to_signals(self, hex_data: str):
        return ' '.join(
            str(-15 + 2*int(hex_symbol,16))
            for hex_symbol in removeprefix(hex_data, "0x"))
