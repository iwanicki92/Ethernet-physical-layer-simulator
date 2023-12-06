from enum import Enum
from typing import Literal, Optional, TypedDict, Union, cast, Dict, Tuple, List
from attr import define

from PyQt5.QtCore import QObject, QThread, pyqtSlot, pyqtSignal, Qt
from PyQt5.QtWidgets import (QMessageBox, QWidget, QVBoxLayout, QHBoxLayout,
                             QFormLayout, QLabel, QSpinBox, QRadioButton,
                             QFrame, QDoubleSpinBox, QComboBox, QPushButton
                             )

import matplotlib
from matplotlib.axes import Axes
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.ticker import EngFormatter

from PySpice.Probe.WaveForm import TransientAnalysis

import numpy

from phyether.dac import DAC
from phyether.gui.util import DoubleSpinBoxNoWheel, SpinBoxNoWheel, create_msg_box
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


@define(kw_only=True, slots=False)
class SimulationArgs(DictMapping):
    init_args: SimulationInitArgs
    run_args: SimulationRunArgs
    input: str


class SimulationDisplay(str, Enum):
    VIN = "vin+, vin-"
    VIN_PLUS = "vin+"
    VIN_MINUS = "vin-"
    VOUT = "vout+, vout-"
    VOUT_PLUS = "vout+"
    VOUT_MINUS = "vout-"


class PairSimulation(QObject):
    simulation_signal = pyqtSignal(TransientAnalysis, float)
    simulation_finished_signal = pyqtSignal()
    error_signal = pyqtSignal()

    def __init__(self, sim_args: List[SimulationArgs]) -> None:
        super().__init__()
        self.sim_args = sim_args

    def simulate_one(self,
                     init_args: SimulationInitArgs,
                     run_args: SimulationRunArgs,
                     input: str):
        twisted_pair = TwistedPair(**init_args)
        symbols = [int(symbol) for symbol in input.split()
                                if symbol.removeprefix('-').isdecimal()]

        try:
            analysis = twisted_pair.simulate(symbols, **run_args)
            self.simulation_signal.emit(analysis, twisted_pair.transmission_delay)
        except Exception:
            self.error_signal.emit()


    @pyqtSlot()
    def simulate(self):
        print("Canvas simulating...")
        for one_sim_args in self.sim_args:
            self.simulate_one(**one_sim_args)
        self.simulation_finished_signal.emit()


class SimulationFormWidget(QFrame):
    def __init__(self, label="Simulation parameters", index = 1):
        super().__init__()
        self.setFrameShape(QFrame.Box)
        self.setLineWidth(1)

        self.form = QWidget()
        self.form_layout = QFormLayout(self.form)

        label_row_widget = QWidget()
        label_row_layout = QHBoxLayout(label_row_widget)
        self.name_label = QLabel(f'{index}. {label}')
        label_row_layout.addWidget(self.name_label)

        self.close_button = QPushButton("X")
        self.close_button.clicked.connect(self.delete)
        self.close_button.setMaximumWidth(30)
        label_row_layout.addWidget(self.close_button, alignment=Qt.AlignRight)

        self.form_layout.addRow(label_row_widget)

        class Parameters(TypedDict):
            label: str
            arg: str
            type: str
            default: object

        self.combobox_widget = QWidget()
        self.combobox_layout = QHBoxLayout()
        self.combobox1 = QComboBox()
        self.combobox2 = QComboBox()
        self.combobox1.addItems(["40GBASE-T", "1000BASE-T"])
        self.combobox2.addItems(["CAT 5e", "Cat 6", "Cat 7"])
        self.combobox_layout.addWidget(self.combobox1)
        self.combobox_layout.addWidget(self.combobox2)
        self.combobox_widget.setLayout(self.combobox_layout)
        self.form_layout.addRow(self.combobox_widget)

        # Create six number inputs using QSpinBox
        self.parameter_labels: List[Parameters] = [
            {"label" : "Rise time [ns]", "arg": "rise_time", "type" : "float", "default": 0.1},
            {"label" : "Signal width [ns]", "arg": "on_time", "type" : "float", "default": 1},
            {"label" : "Voltage offset [V]", "arg": "voltage_offset", "type" : "float", "default": 0},
            {"label" : "Output impedance [Ohm]", "arg": "output_impedance", "type" : "float", "default": 100},
            {"label" : "Length [m]", "arg": "length", "type" : "int", "default": 2},
            {"label" : "Resistance [Ohm]", "arg": "resistance", "type" : "float", "default": 0.188},
            {"label" : "Inductance [H]", "arg": "inductance", "type" : "float", "default": 525},
            {"label" : "Capacitance [F]", "arg": "capacitance", "type" : "float", "default": 52},
        ]
        self.number_inputs: Dict[str, Union[QDoubleSpinBox, QSpinBox]] = {}
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
        self.lossy_option = QRadioButton("lossy")
        self.lossy_option.setChecked(True)
        self.lossless_option = QRadioButton("lossless")
        self.radio_layout.addWidget(self.lossy_option)
        self.radio_layout.addWidget(self.lossless_option)
        self.radio_button.setLayout(self.radio_layout)
        self.form_layout.addRow("Select an option:", self.radio_button)

        self.frame_layout = QVBoxLayout(self)
        self.frame_layout.addWidget(self.form)

        print(f"Created SimulationFormWidget, label = {label}")

    def delete(self):
        print("Deleteing form...")
        self.setParent(None)

class SimulatorCanvas(FigureCanvasQTAgg):
    simulation_stopped_signal = pyqtSignal()

    def __init__(self, *, init_axes = True):
        super().__init__()
        if init_axes:
            self.axes: Axes = cast(Axes, self.figure.subplots(1, 1))
            self.axes.grid(True)
            self.draw()
        self.figure.text(0.5, 0.04, 'Time', ha='center')
        self.figure.text(0.04, 0.5, 'Voltage (V)', va='center', rotation='vertical')
        print("Created canvas")

        self.simulation: Optional[PairSimulation] = None
        self.thread: QThread = QThread(self)
        self.simulations: List[Tuple[TransientAnalysis, float]] = []
        self._display_params: List[SimulationDisplay] = []
        self.plots: Dict[SimulationDisplay, bool] = {}

    def set_display_params(self, display_params: List[SimulationDisplay]):
        self._display_params = display_params
        self._draw_plot()

    def _add_simulation(self, analysis: TransientAnalysis, transmission_delay: float):
        index = len(self.simulations)
        self.simulations.append((analysis, transmission_delay))
        print(f"Draw simulation: {index + 1}")
        self._draw_add(self.simulations[-1], index)

    def _get_vin_x(self, analysis, delay):
        return analysis.time[analysis.time<(analysis.time[-1] - delay)]

    def _draw_add(self,
                  simulation: Tuple[TransientAnalysis, float],
                  index: int):
        analysis, transmission_delay = simulation
        for display_param in self._display_params:
            plot_x = None
            plot_y = None

            if display_param == SimulationDisplay.VIN:
                plot_x = self._get_vin_x(analysis, transmission_delay)
                plot_y = (analysis['vin+'] - analysis['vin-'])[:len(plot_x)]
            elif display_param == SimulationDisplay.VOUT:
                plot_x = cast(numpy.ndarray, analysis.time - transmission_delay)
                plot_x = plot_x[plot_x>=0]
                plot_y = (analysis['vout+'] - analysis['vout-'])[-len(plot_x):]
            elif display_param == SimulationDisplay.VIN_PLUS:
                plot_x = self._get_vin_x(analysis, transmission_delay)
                plot_y = analysis['vin+'][:len(plot_x)]
            elif display_param == SimulationDisplay.VIN_MINUS:
                plot_x = plot_x = self._get_vin_x(analysis, transmission_delay)
                plot_y = analysis['vin-'][:len(plot_x)]
            elif display_param == SimulationDisplay.VOUT_PLUS:
                plot_x = cast(numpy.ndarray, analysis.time - transmission_delay)
                plot_x = plot_x[plot_x>=0]
                plot_y = analysis['vout+'][-len(plot_x):]
            elif display_param == SimulationDisplay.VOUT_MINUS:
                plot_x = cast(numpy.ndarray, analysis.time - transmission_delay)
                plot_x = plot_x[plot_x>=0]
                plot_y = analysis['vout-'][-len(plot_x):]

            if plot_x is not None and plot_y is not None:
                plot_y = plot_y[:len(plot_x)]
                self.axes.plot(plot_x, plot_y,
                               label=f'sim {index}: {display_param.value}')
        self.axes.legend()
        self.draw()

    def _draw_plot(self):
        self.clear_plot()
        for index, simulation in enumerate(self.simulations):
            self._draw_add(simulation, index)

    def simulation_error(self):
        create_msg_box("There was error during simulation, change parameters", "error")
        self._stop_simulation()

    def _stop_simulation(self):
        print("Simulation finished")
        self.thread.exit()
        self.simulation_stopped_signal.emit()

    def simulate(self, sim_args: List[SimulationArgs]):
        print("Simulating")
        self.simulations.clear()
        self.simulating = True
        self.clear_plot()
        self.simulation = PairSimulation(sim_args)
        self.thread = QThread(self)
        self.simulation.simulation_signal.connect(self._add_simulation)
        self.simulation.error_signal.connect(self.simulation_error)
        self.simulation.simulation_finished_signal.connect(self._stop_simulation)
        self.simulation.moveToThread(self.thread)
        self.thread.started.connect(self.simulation.simulate) # type: ignore
        self.thread.start()

    def clear_plot(self):
        print("Canvas clearing...")
        self.axes.cla()
        self.axes.grid()
        self.axes.xaxis.set_major_formatter(EngFormatter(unit='s'))
