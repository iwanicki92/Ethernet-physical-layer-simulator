from typing import Iterable, Literal, Optional, overload
from PySpice.Probe.WaveForm import TransientAnalysis

from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import u_V, u_s

from phyether.dac import DAC
from phyether.twisted_pair import TwistedPair


class EthernetCable:

    @overload
    def __init__(self, *,
                 dac: DAC,
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
                 ) -> None:
        """Losseless transmission line

        :param dac: Digital to Analog Converter
        :param transmission_type: lossless transmision line
        :param output_impedance: In Ω, defaults to 100
        :param characteristic_impedance: In Ω, defaults to 100
        :param transmission_delay: In ns. Delay must be >0, defaults to 5
        """

    def __init__(self, **kwargs) -> None:
        self.circuit = Circuit("Ethernet Cable")
        self.A = TwistedPair(**kwargs, name="A")
        self.B = TwistedPair(**kwargs, name="B")
        self.C = TwistedPair(**kwargs, name="C")
        self.D = TwistedPair(**kwargs, name="D")
        self.pairs = {self.A, self.B, self.C, self.D}
        self.transmission_delay = self.A.delay
        for pair in self.pairs:
            self.circuit.subcircuit(pair)
            self.circuit.X(pair.name, f'{pair.name}', f'{pair.name}_vin+', f'{pair.name}_vin-',
                       f'{pair.name}_vout+', f'{pair.name}_vout-', 'offset+')

    def simulate(self,
                 data: tuple[Iterable[int], Iterable[int],
                             Iterable[int], Iterable[int]],
                 presimulation_ratio: int = 0,
                 voltage_offset: float = 0) -> TransientAnalysis:
        """_summary_

        :param data: Symbol data to send over twisted pair.
        :param presimulation_ratio: Simulate ratio * transmission_delay worth of signals beforehand, defaults to 0
        :param voltage_offset: Voltage offset of one pair relative to ground, defaults to 0
        :return: Transient analysis simulation
        """
        self.circuit.VoltageSource(f'offset', 'offset+', self.circuit.gnd, u_V(voltage_offset))
        end_time = u_s(0)
        start_time = u_s(0)
        for pair, pair_data in zip(self.pairs, data):
            presignals, pwl = pair._get_pwl(pair_data, presimulation_ratio)
            end_time = pwl[-1][0] + pair.transmission_delay + pair.dac.rise_time
            start_time = presignals * pair.dac.symbol_time
            self.circuit.PieceWiseLinearVoltageSource(
                f'{pair.name}signal', f'{pair.name}_vin+',
                f'{pair.name}_vin-', values = pwl)

        step_time = self.A.dac.rise_time / 10
        simulator = self.circuit.simulator(temperature=25,
            nominal_temperature=25,
            simulator="ngspice-shared")
        simulation = simulator.transient(
            step_time=step_time,
            end_time=end_time,
            start_time=start_time)
        simulation._time = simulation.time.as_ndarray() - simulation._time[0]

        self.circuit.Voffset.detach()
        for pair in self.pairs:
            self.circuit[f'V{pair.name}signal'].detach()

        return simulation
