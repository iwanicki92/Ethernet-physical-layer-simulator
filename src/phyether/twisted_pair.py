from typing import Iterable

from PySpice.Logging import Logging
from PySpice.Probe.WaveForm import TransientAnalysis
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *  # pylint: disable=unused-wildcard-import, wildcard-import

from phyether.dac import DAC

Logging.setup_logging(logging_level='ERROR')


class TwistedPair:
    def __init__(self, *,
                 dac: DAC,
                 characteristic_impedance: float = 100,
                 output_impedance: float = 100,
                 transmission_delay: float = 5,
                 ) -> None:
        """_summary_

        Args:
            dac (DAC): Digital to Analog Converter.
            characteristic_impedance (float, optional): In Ω
            output_impedance (float, optional): In Ω
            transmission_delay (float, optional): In ns. Delay must be >0
        """
        # Simulated circuit will double voltage values
        dac.quotient /= 2
        self.dac = dac
        self.transmission_delay = u_ns(transmission_delay)
        circuit = Circuit('Twisted Pair')
        circuit.R('positiveR', 'vin+', 'vout+', u_GOhm(1))
        circuit.R('negativeR', 'vout-', 'vin-', u_GOhm(1))
        circuit.R('load', 'vout+', 'vout-', u_Ohm(output_impedance))
        circuit.LosslessTransmissionLine('tline', 'vin+', 'vin-', 'vout+', 'vout-',
                                         impedance=u_Ohm(characteristic_impedance),
                                         time_delay=u_ns(transmission_delay))
        self.circuit = circuit

    def simulate(self, data: Iterable[int]) -> TransientAnalysis:
        """_summary_

        Args:
            data (Iterable[int]): Symbol data to send over twisted pair.

        Returns:
            TransientAnalysis: transient analysis simulation
        """
        pwl = self.dac.to_pwl(data)
        end_time = pwl[-1][0] + self.transmission_delay + self.dac.rise_time
        step_time = self.dac.rise_time / 10
        self.circuit.PieceWiseLinearVoltageSource('positivePair',
                                                  'vin+',
                                                  self.circuit.gnd,
                                                  values=pwl)
        self.circuit.PieceWiseLinearVoltageSource('negativePair',
                                                  self.circuit.gnd,
                                                  'vin-',
                                                  values=pwl)
        simulator = self.circuit.simulator(temperature=25,
                                           nominal_temperature=25,
                                           simulator="ngspice-shared")
        simulation = simulator.transient(step_time=step_time, end_time=end_time)
        self.circuit.VpositivePair.detach()
        self.circuit.VnegativePair.detach()
        return simulation
