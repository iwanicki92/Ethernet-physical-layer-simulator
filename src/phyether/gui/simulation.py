from typing import Literal, TypedDict, Union, cast
from attr import define

from PyQt5.QtCore import QObject, QThread, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import (QMessageBox, QWidget, QVBoxLayout, QHBoxLayout,
                             QFormLayout, QLabel, QSpinBox, QRadioButton,
                             QFrame, QDoubleSpinBox,
                             )

import matplotlib
from matplotlib.axes import Axes
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.ticker import EngFormatter

from PySpice.Probe.WaveForm import TransientAnalysis, WaveForm

import numpy

from phyether.dac import DAC
from phyether.gui.util import DoubleSpinBoxNoWheel, SpinBoxNoWheel
from phyether.twisted_pair import TwistedPair
from phyether.util import DictMapping

matplotlib.use('QtAgg')


@define(kw_only=True, slots=False)
class SimulationInitArgs(DictMapping):
    dac: DAC
    transmission_type: Literal['lossy', 'lossless']
    output_impedance: float = 100
    characteristic_impedance: float = 100
    length: int = 1
    resistance: float = 0.188
    inductance: float = 525
    capacitance: float = 52
    transmission_delay: float = 5


@define(kw_only=True, slots=False)
class SimulationRunArgs(DictMapping):
    presimulation_ratio: int = 2
    voltage_offset: int = 0


class PairSimulation(QObject):
    simulation_signal = pyqtSignal(TransientAnalysis, float)
    error_signal = pyqtSignal()

    def __init__(self, init_args: SimulationInitArgs,
                 run_args: SimulationRunArgs,
                 input: str) -> None:
        super().__init__()
        self.init_args = init_args
        self.run_args = run_args
        self.input = input

    @pyqtSlot()
    def simulate(self):
        print("Canvas simulating...")
        twisted_pair = TwistedPair(**self.init_args)
        symbols = [int(symbol) for symbol in self.input.split()
                                if symbol.removeprefix('-').isdecimal()]

        try:
            analysis = twisted_pair.simulate(symbols, **self.run_args)
            self.simulation_signal.emit(analysis, twisted_pair.transmission_delay)
        except Exception:
            self.error_signal.emit()


class SimulationFormWidget(QFrame):
    def __init__(self, label="Simulation parameters", index = 1):
        super().__init__()
        self.setFrameShape(QFrame.Box)
        self.setLineWidth(1)

        self.form = QWidget()
        self.form_layout = QFormLayout(self.form)

        self.form_layout.addRow(QLabel(f'{index}. {label}'))

        class Parameters(TypedDict):
            label: str
            arg: str
            type: str
            default: object

        # Create six number inputs using QSpinBox
        self.parameter_labels: list[Parameters] = [
            {"label" : "Voltage offset", "arg": "voltage_offset", "type" : "float", "default": 0},
            {"label" : "Output impedance", "arg": "output_impedance", "type" : "float", "default": 100},
            {"label" : "Length", "arg": "length", "type" : "int", "default": 2},
            {"label" : "Resistance", "arg": "resistance", "type" : "float", "default": 0.188},
            {"label" : "Inductance", "arg": "inductance", "type" : "float", "default": 525},
            {"label" : "Capacitance", "arg": "capacitance", "type" : "float", "default": 52},
        ]
        self.number_inputs: dict[str, Union[QDoubleSpinBox, QSpinBox]] = {}
        for i, parameter in enumerate(self.parameter_labels):
            arg = parameter["arg"]
            if parameter["type"] == "float":
                self.number_inputs[arg] = DoubleSpinBoxNoWheel()
            elif parameter["type"] == "int":
                self.number_inputs[arg] = SpinBoxNoWheel()
            self.number_inputs[arg].setMaximum(1000)
            self.number_inputs[arg].setValue(parameter['default']) # type: ignore
            self.form_layout.addRow(parameter['label'], self.number_inputs[arg])

        self.radio_button = QWidget()
        self.radio_layout = QHBoxLayout()
        self.option1 = QRadioButton("lossy")
        self.option1.setChecked(True)
        self.radio_layout.addWidget(self.option1)
        self.radio_button.setLayout(self.radio_layout)
        self.form_layout.addRow("Select an option:", self.radio_button)

        self.frame_layout = QVBoxLayout(self)
        self.frame_layout.addWidget(self.form)

        print(f"Created SimulationFormWidget, label = {label}")

class SimulatorCanvas(FigureCanvasQTAgg):
    simulation_stopped_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.axes: Axes = cast(Axes, self.figure.subplots (1, 1))
        self.figure.text(0.5, 0.04, 'Time', ha='center')
        self.figure.text(0.04, 0.5, 'Voltage (V)', va='center', rotation='vertical')
        self.axes.grid(True)
        self.draw()
        print("Created canvas")

        self.simulation: Union[PairSimulation, None] = None
        self.thread: QThread = QThread(self)

    def draw_plot(self, analysis: TransientAnalysis, transmission_delay: float):
        v_in: WaveForm = analysis['vin+'] - analysis['vin-']
        v_out: WaveForm = analysis['vout+'] - analysis['vout-']

        vx_out_transformed = cast(numpy.ndarray, analysis.time - transmission_delay)
        vx_out_transformed = vx_out_transformed[vx_out_transformed>=0]
        # trim v_in where nothing happens after shifting v_out
        vx_in_transformed = analysis.time[
            analysis.time<(analysis.time[-1] - transmission_delay)]

        self.axes.plot(
            vx_in_transformed,
            v_in[:len(vx_in_transformed)],
            'blue',
            vx_out_transformed,
            v_out[-len(vx_out_transformed):],
            'red'
        )
        self.axes.legend(['v(in+, in-)', 'v(out+, out-)'], loc='upper right')
        self.draw()
        self._stop_simulation()

    def simulation_error(self):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setText("There was error during simulation, change parameters")
        msg_box.setWindowTitle("Error")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
        self._stop_simulation()

    def _stop_simulation(self):
        self.thread.exit()
        self.simulation_stopped_signal.emit()

    def simulate(self, input: str, index: int,
                 init_args: SimulationInitArgs, run_args: SimulationRunArgs):
        if self.thread.isRunning():
            self.thread.requestInterruption()
            self.thread.exit()
            return

        self.simulation = PairSimulation(init_args=init_args,
                                         run_args=run_args,
                                         input=input)
        self.thread = QThread(self)
        self.simulation.simulation_signal.connect(self.draw_plot)
        self.simulation.error_signal.connect(self.simulation_error)
        self.simulation.moveToThread(self.thread)
        self.thread.started.connect(self.simulation.simulate) # type: ignore
        self.thread.start()

    def clear_plot(self):
        print("Canvas clearing...")
        self.axes.cla()
        self.axes.grid()
        self.axes.set_ylim(-3, 3)
        self.axes.xaxis.set_major_formatter(EngFormatter(unit='s'))
