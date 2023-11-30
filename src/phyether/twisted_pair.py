from math import sqrt
import random
from typing import Iterable, Literal, Optional, Sequence, overload, Tuple

from PySpice.Logging import Logging
from PySpice.Probe.WaveForm import TransientAnalysis
from PySpice.Spice.Netlist import Circuit, SubCircuit, SubCircuitFactory
from PySpice.Unit import *
from PySpice.Unit.Unit import UnitValue  # pylint: disable=unused-wildcard-import, wildcard-import

from phyether.dac import DAC

Logging.setup_logging(logging_level='DEBUG')

class TwistedPair(SubCircuit):
    __nodes__ = ('vin+', 'vin-', 'vout+', 'vout-', 'offset+')

    @property
    def delay(self):
        return self.transmission_delay

    @overload
    def __init__(self, *,
                 dac: DAC,
                 output_impedance: float = 100,
                 length: int = 1,
                 resistance: float = 0.188,
                 inductance: float = 525,
                 capacitance: float = 52,
                 transmission_type: Literal['lossy'],
                 name: str = "pair"
                 ) -> None:
        """Lossy transmission line

        transmission delay = length * sqrt(inductance * capacitance)

        :param dac: Digital to Analog Converter
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
                 output_impedance: float = 100,
                 characteristic_impedance: float = 100,
                 transmission_delay: float = 5,
                 transmission_type: Literal['lossless'],
                 name: str = "pair"
                 ) -> None:
        """Losseless transmission line

        :param dac: Digital to Analog Converter
        :param transmission_type: lossless transmision line
        :param output_impedance: In Ω, defaults to 100
        :param characteristic_impedance: In Ω, defaults to 100
        :param transmission_delay: In ns. Delay must be >0, defaults to 5
        """

    def __init__(self, *,
                 dac: DAC,
                 output_impedance: float = 100,
                 characteristic_impedance: Optional[float] = 100,
                 length: Optional[int] = 1,
                 resistance: Optional[float] = 0.188,
                 inductance: Optional[float] = 525,
                 capacitance: Optional[float] = 52,
                 transmission_delay: Optional[float] = 5,
                 transmission_type: Literal['lossy', 'lossless'],
                 name: str = "pair"
                 ) -> None:
        SubCircuit.__init__(self, name, *self.__nodes__)
        self.dac = dac
        self.R('positiveR', 'vin+', 'vout+', u_GOhm(1000))
        self.R('negativeR', 'vout-', 'vin-', u_GOhm(1000))
        self.R('load', 'vout+', 'vout-', u_Ohm(output_impedance))
        self.transmission_delay: UnitValue
        if transmission_type == 'lossy':
            self.transmission_delay = length * u_ns(u_s(sqrt(u_nH(inductance) * u_pF(capacitance))))
            self.raw_spice = "O1 vin+ vin- vout+ vout- ltra"
            self.raw_spice += f"\n.model ltra ltra LEN={length} R={resistance} L={inductance}n C={capacitance}p"
        else:
            self.transmission_delay = u_ns(transmission_delay)
            self.LosslessTransmissionLine(
                'tline', 'vin+', 'vin-', 'vout+', 'vout-',
                impedance=u_Ohm(characteristic_impedance),
                time_delay=self.transmission_delay)
        self.R('res+', 'vin+', 'offset+', u_GOhm(1000))
        self.R('res-', 'offset+', 'vin-', u_GOhm(1000))

    def _get_pwl(self, data: Iterable[int],
                 presimulation_ratio: int
                 ) -> Tuple[int, Sequence[Tuple[UnitValue, UnitValue]]]:
        presignals = 0
        data_to_simulate = data
        if presimulation_ratio:
            presignals = int(presimulation_ratio * self.delay/self.dac.symbol_time) + 5
            data_to_simulate = self.dac.random_signals(presignals)
            data_to_simulate.extend(data)
        return presignals, self.dac.to_pwl(data_to_simulate)

    def simulate(self, data: Iterable[int], presimulation_ratio: int = 0,
                 voltage_offset: float = 0) -> TransientAnalysis:
        """_summary_

        :param data: Symbol data to send over twisted pair.
        :param presimulation_ratio: Simulate ratio * transmission_delay worth of signals beforehand, defaults to 0
        :param voltage_offset: Voltage offset of one pair relative to ground, defaults to 0
        :return: Transient analysis simulation
        """
        circuit = Circuit("Twisted Pair")
        circuit.VoltageSource(f'offset', 'offset+', self.gnd, u_V(voltage_offset))
        circuit.subcircuit(self)
        circuit.X(1, 'pair', 'vin+', 'vin-', 'vout+', 'vout-', 'offset+')
        presignals, pwl = self._get_pwl(data, presimulation_ratio)
        self.PieceWiseLinearVoltageSource('signal', 'vin+', 'vin-', values = pwl)
        end_time = pwl[-1][0] + self.transmission_delay + self.dac.rise_time
        step_time = self.dac.rise_time / 10
        simulator = circuit.simulator(temperature=25,
                                           nominal_temperature=25,
                                           simulator="ngspice-shared")
        simulation = simulator.transient(
            step_time=step_time,
            end_time=end_time,
            start_time=presignals * self.dac.symbol_time)
        simulation._time = simulation.time.as_ndarray() - simulation._time[0]
        self.Vsignal.detach()
        return simulation
