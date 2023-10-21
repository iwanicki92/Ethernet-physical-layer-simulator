from math import sqrt
import random
from typing import Iterable, Literal, Optional,  overload

from PySpice.Logging import Logging
from PySpice.Probe.WaveForm import TransientAnalysis
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
from PySpice.Unit.Unit import UnitValue  # pylint: disable=unused-wildcard-import, wildcard-import

from phyether.dac import DAC

Logging.setup_logging(logging_level='DEBUG')


class TwistedPair:
    @property
    def delay(self):
        return self.transmission_delay

    @overload
    def __init__(self, *,
                 dac: DAC,
                 voltage_offset: float = 0,
                 output_impedance: float = 100,
                 length: int = 1,
                 resistance: float = 0.188,
                 inductance: float = 525,
                 capacitance: float = 52,
                 transmission_type: Literal['lossy'],
                 ) -> None:
        """Lossy transmission line

        transmission delay = length * sqrt(inductance * capacitance)

        :param dac: Digital to Analog Converter
        :param voltage_offset: Voltage offset of one pair relative to ground, defaults to 0
        :param transmission_type: lossy transmission line
        :param output_impedance: In Ω, defaults to 100
        :param length: length of twisted pair in meters, defaults to 1
        :param resistance: resistance per meter, defaults to 0.188 Ω
        :param inductance: inductance per meter, defaults to 525 nH
        :param capacitance: capacitance per meter, defaults to 52 pF
        """

    @overload
    def __init__(self, *,
                 dac: DAC,
                 voltage_offset: float = 0,
                 output_impedance: float = 100,
                 characteristic_impedance: float = 100,
                 transmission_delay: float = 5,
                 transmission_type: Literal['lossless'],
                 ) -> None:
        """Losseless transmission line

        :param dac: Digital to Analog Converter
        :param voltage_offset: Voltage offset of one pair relative to ground, defaults to 0
        :param transmission_type: lossless transmision line
        :param output_impedance: In Ω, defaults to 100
        :param characteristic_impedance: In Ω, defaults to 100
        :param transmission_delay: In ns. Delay must be >0, defaults to 5
        """

    def __init__(self, *,
                 dac: DAC,
                 voltage_offset: float = 0,
                 output_impedance: float = 100,
                 characteristic_impedance: Optional[float] = 100,
                 length: Optional[int] = 1,
                 resistance: Optional[float] = 0.188,
                 inductance: Optional[float] = 525,
                 capacitance: Optional[float] = 52,
                 transmission_delay: Optional[float] = 5,
                 transmission_type: Literal['lossy', 'lossless'],
                 ) -> None:
        self.dac = dac
        circuit = Circuit('Twisted Pair')
        circuit.R('positiveR', 'vin+', 'vout+', u_GOhm(1000))
        circuit.R('negativeR', 'vout-', 'vin-', u_GOhm(1000))
        circuit.R('load', 'vout+', 'vout-', u_Ohm(output_impedance))
        self.transmission_delay: UnitValue
        if transmission_type == 'lossy':
            self.transmission_delay = length * u_ns(u_s(sqrt(u_nH(inductance) * u_pF(capacitance))))
            circuit.raw_spice = "O1 vin+ vin- vout+ vout- ltra"
            circuit.raw_spice += f"\n.model ltra ltra LEN={length} R={resistance} L={inductance}n C={capacitance}p"
        else:
            self.transmission_delay = u_ns(transmission_delay)
            circuit.LosslessTransmissionLine(
                'tline', 'vin+', 'vin-', 'vout+', 'vout-',
                impedance=u_Ohm(characteristic_impedance),
                time_delay=self.transmission_delay)
        circuit.R('res+', 'vin+', 'offset+', u_GOhm(1000))
        circuit.R('res-', 'vin-', 'offset+', u_GOhm(1000))
        circuit.VoltageSource('offset', 'offset+', circuit.gnd, u_V(voltage_offset))
        self.circuit = circuit

    def simulate(self, data: Iterable[int], presimulation_ratio = 0) -> TransientAnalysis:
        """_summary_

        :param data: Symbol data to send over twisted pair.
        :param presimulation_ratio: Simulate ratio * transmission_delay worth of signals beforehand, defaults to 0
        :return: Transient analysis simulation
        """
        data_to_simulate = data
        presignals = 0
        if presimulation_ratio:
            presignals = int(presimulation_ratio * self.delay/self.dac.symbol_time) + 5
            possible_symbols = range(-self.dac.high_symbol, self.dac.high_symbol)
            data_to_simulate = random.choices(
                possible_symbols,
                k=presignals - 1
                ) + [0]
            data_to_simulate.extend(data)
        pwl = self.dac.to_pwl(data_to_simulate)
        self.circuit.PieceWiseLinearVoltageSource('signal',
                                                  'vin+',
                                                  'vin-',
                                                  values = pwl)
        end_time = pwl[-1][0] + self.transmission_delay + self.dac.rise_time
        step_time = self.dac.rise_time / 10
        simulator = self.circuit.simulator(temperature=25,
                                           nominal_temperature=25,
                                           simulator="ngspice-shared")
        simulation = simulator.transient(
            step_time=step_time,
            end_time=end_time,
            start_time=presignals * self.dac.symbol_time)
        simulation._time = simulation.time.as_ndarray() - simulation._time[0]
        self.circuit.Vsignal.detach()
        return simulation
