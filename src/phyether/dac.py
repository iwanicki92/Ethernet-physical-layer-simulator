from __future__ import annotations
import random
from typing import Iterable, Optional, Sequence, List, Tuple

from PySpice.Unit import *
from PySpice.Unit.Unit import UnitValue  # pylint: disable=unused-wildcard-import, wildcard-import


class DAC:
    """Digital to analog converter

    Converts digital symbols to voltages or piecewise linear function
    """

    def __init__(self, rise_time: float, on_time: float, high_symbol: int,
                 symbol_step: int = 1, max_voltage: float = 2,
                 attenuation: Optional[Attenuation] = None) -> None:
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
        # in MHz
        frequency = 1e-6 / (self.rise_time + self.on_time)
        if attenuation is not None:
            self.attenuation = attenuation
            self.loss_per_meter = attenuation.calculate_attenuation(frequency) / 100
        else:
            self.attenuation = NoLossCable()
            self.loss_per_meter = 0
        self.quotient = max_voltage / high_symbol
        self.symbol_step = symbol_step

    @property
    def symbol_time(self) -> UnitValue:
        return self.rise_time + self.on_time

    @property
    def possible_symbols(self) -> range:
        return range(-self.high_symbol, self.high_symbol+1, self.symbol_step)

    def signal_after_loss(self, signal, cable_length):
        return self.attenuation.calculate_signal(self.loss_per_meter * cable_length, signal)

    def to_voltage(self, data: Iterable[int]) -> Iterable[UnitValue]:
        """Change digital data into voltages.

        Args:
            data (Iterable[int]): digital symbol data e.g [-2, -1, 0, 1, 2]

        Returns:
            Iterable[float]: data as voltages
        """
        return [u_V(symbol * self.quotient) for symbol in data]

    def to_pwl(self, data: Iterable[int]) -> Sequence[Tuple[UnitValue, UnitValue]]:
        """Turn data into PWL form.

        Args:
            data (Iterable[int]): digital data

        Returns:
            Sequence[Tuple[float, float]]: PWL data
        """
        voltages = self.to_voltage(data)
        pwl: List[Tuple[UnitValue, UnitValue]] = [(u_ns(0), u_V(0))]
        time = self.rise_time
        for voltage in voltages:
            pwl.append((time, u_V(voltage)))
            pwl.append((time + self.on_time, u_V(voltage)))
            time = time + self.symbol_time
        pwl.append((time, u_V(0)))

        return pwl

    def random_signals(self, number_of_signals: int) -> List[int]:
            return random.choices(
                self.possible_symbols,
                k=number_of_signals - 1
                ) + [0]


class Attenuation:
    def __init__(self, k1: float, k2: float, k3: float) -> None:
        """constructor
        :param attenuation: List of attenuations per different frequencies: [(MHz, dB)]
        """
        self.k1 = k1
        self.k2 = k2
        self.k3 = k3

    def calculate_signal(self, attenuation: float, signal):
        return signal / (10**(attenuation / 20))


    def calculate_attenuation(self, frequency: float) -> float:
        """Calculate attenuation for specified frequency

        :param frequency: signal frequency
        :return: attenuation in dB per 100m
        """
        if frequency == 0:
            return 0
        return self.k1*(frequency**(1/2)) + self.k2*frequency + self.k3/(frequency**(1/2))


def NoLossCable():
    return Attenuation(0,0,0)

def Cat5():
    return Attenuation(1.9108, 0.0222, 0.2)

def Cat5e():
    return Attenuation(1.967, 0.023, 0.05)

def Cat6():
    return Attenuation(1.82, 0.0169, 0.25)

def Cat7():
    return Attenuation(1.8, 0.01, 0.2)
