import random
from typing import Iterable, Optional, Sequence

from PySpice.Unit import *
from PySpice.Unit.Unit import UnitValue  # pylint: disable=unused-wildcard-import, wildcard-import


class DAC:
    """Digital to analog converter

    Converts digital symbols to voltages or piecewise linear function
    """

    def __init__(self, rise_time: float, on_time: float,
                 high_symbol: int, symbol_step: int = 1, max_voltage: float = 2) -> None:
        """Convert symbols from digital to analog (piecewise linear)

        Formula for symbol to voltage conversion:
            voltage = symbol * max_voltage / high_symbol

        Args:
            rise_time (float): time to change from one voltage to another in nanoseconds
            on_time (float): duration of one symbol in nanoseconds
            high_symbol (int): highest symbol value in data
            max_voltage (float): voltage for max_symbol
            symbol_step (int): difference between adjacent symbols
        """
        self.rise_time: UnitValue = u_ns(rise_time)
        self.on_time: UnitValue = u_ns(on_time)
        self.high_symbol = high_symbol
        self.quotient = max_voltage / high_symbol
        self.symbol_step = symbol_step

    @property
    def symbol_time(self) -> UnitValue:
        return self.rise_time + self.on_time

    @property
    def possible_symbols(self) -> range:
        return range(-self.high_symbol, self.high_symbol+1, self.symbol_step)

    def to_voltage(self, data: Iterable[int]) -> Iterable[UnitValue]:
        """Change digital data into voltages.

        Args:
            data (Iterable[int]): digital symbol data e.g [-2, -1, 0, 1, 2]

        Returns:
            Iterable[float]: data as voltages
        """
        return [u_V(symbol * self.quotient) for symbol in data]

    def to_pwl(self, data: Iterable[int]) -> Sequence[tuple[UnitValue, UnitValue]]:
        """Turn data into PWL form.

        Args:
            data (Iterable[int]): digital data

        Returns:
            Sequence[tuple[float, float]]: PWL data
        """
        voltages = self.to_voltage(data)
        pwl: list[tuple[UnitValue, UnitValue]] = [(u_ns(0), u_V(0))]
        time = self.rise_time
        for voltage in voltages:
            pwl.append((time, u_V(voltage)))
            pwl.append((time + self.on_time, u_V(voltage)))
            time = time + self.symbol_time
        pwl.append((time, u_V(0)))

        return pwl

    def random_signals(self, number_of_signals: int) -> list[int]:
            return random.choices(
                self.possible_symbols,
                k=number_of_signals - 1
                ) + [0]
