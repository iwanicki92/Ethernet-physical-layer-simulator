from typing import Iterable, Sequence

from PySpice.Unit import *  # pylint: disable=unused-wildcard-import, wildcard-import


class DAC:
    def __init__(self, rise_time: float, on_time: float,
                 high_symbol: int, max_voltage: int = 2) -> None:
        """Convert symbols from digital to analog (piecewise linear)

        Formula for symbol to voltage conversion:
            voltage = symbol * max_voltage / high_symbol

        Args:
            rise_time (float): time to change from one voltage to another in nanoseconds
            on_time (float): duration of one symbol in nanoseconds
            high_symbol (int): highest symbol value in data
            max_voltage (int): voltage for max_symbol
        """
        self.rise_time = u_ns(rise_time)
        self.on_time = u_ns(on_time)
        self.quotient = max_voltage / high_symbol

    def to_voltage(self, data: Iterable[int]) -> Iterable[float]:
        """Change digital data into voltages.

        Args:
            data (Iterable[int]): digital symbol data e.g [-2, -1, 0, 1, 2]

        Returns:
            Iterable[float]: data as voltages
        """
        return [u_V(symbol * self.quotient) for symbol in data]

    def to_pwl(self, data: Iterable[int]) -> Sequence[tuple[float, float]]:
        """Turn data into PWL form.

        Args:
            data (Iterable[int]): digital data

        Returns:
            Sequence[tuple[float, float]]: PWL data
        """
        voltages = self.to_voltage(data)
        pwl: list[tuple[float, float]] = [(0, 0)]
        time = self.rise_time
        for voltage in voltages:
            pwl.append((time, voltage))
            pwl.append((time + self.on_time, voltage))
            time = time + self.on_time + self.rise_time
        pwl.append((time, 0))

        return pwl
