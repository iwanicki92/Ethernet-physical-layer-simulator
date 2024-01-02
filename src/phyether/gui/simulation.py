from enum import Enum
from typing import Literal, NamedTuple, Optional, TypedDict, Union, cast, Dict, Tuple, List
from attr import define

from PyQt5.QtCore import QObject, QThread, pyqtSlot, pyqtSignal, Qt
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QFormLayout, QLabel, QSpinBox, QRadioButton,
                             QFrame, QDoubleSpinBox, QComboBox, QPushButton
                             )

import matplotlib
from matplotlib.axes import Axes
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.ticker import EngFormatter

from PySpice.Probe.WaveForm import TransientAnalysis

import numpy

from phyether.dac import DAC, Attenuation, Cat5, Cat5e, Cat6, Cat7
from phyether.gui.util import DoubleSpinBoxNoWheel, SpinBoxNoWheel, create_msg_box
from phyether.twisted_pair import TwistedPair
from phyether.util import DictMapping, removeprefix

matplotlib.use('QtAgg')


@define(kw_only=True, slots=False)
class SimulationInitArgs(DictMapping):
    dac: DAC
    transmission_type: Literal['lossy', 'lossless'] = 'lossy'
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
    index: str


class SimulationDisplay(str, Enum):
    VIN = "vin+, vin-"
    VIN_PLUS = "vin+"
    VIN_MINUS = "vin-"
    VOUT = "vout+, vout-"
    VOUT_PLUS = "vout+"
    VOUT_MINUS = "vout-"


class PairSimulation(QObject):
    simulation_signal = pyqtSignal(TransientAnalysis, float, str)
    simulation_finished_signal = pyqtSignal()
    error_signal = pyqtSignal()

    def __init__(self, sim_args: List[SimulationArgs]) -> None:
        super().__init__()
        self.sim_args = sim_args

    def simulate_one(self,
                     init_args: SimulationInitArgs,
                     run_args: SimulationRunArgs,
                     input: str,
                     index: str):
        twisted_pair = TwistedPair(**init_args)
        symbols = [int(symbol) for symbol in input.split()
                                if removeprefix(symbol, '-').isdecimal()]

        try:
            analysis = twisted_pair.simulate(symbols, **run_args)
            self.simulation_signal.emit(analysis, twisted_pair.transmission_delay, index)
        except Exception as e:
            print(f"Error: {e}")
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
            min: float
            max: float

        self.cable_mapping: Dict[str, Attenuation] = {
                "Cat5": Cat5(),
                "Cat5e": Cat5e(),
                "Cat6": Cat6(),
                "Cat7": Cat7(),
            }

        class StandardSpeed(NamedTuple):
            rise_time: float
            on_time: float

        self.standards_mapping: Dict[str, StandardSpeed] = {
                "40GBASE-T": StandardSpeed(0.1, 0.625),
                "10GBASE-T": StandardSpeed(0.1, 1.2),
                "1000BASE-T": StandardSpeed(2, 8)
            }

        self.combobox_widget = QWidget()
        self.combobox_layout = QHBoxLayout()
        self.standards_combobox = QComboBox()
        self.cable_combobox = QComboBox()
        self.standards_combobox.addItems(self.standards_mapping.keys())
        self.standards_combobox.currentTextChanged.connect(self.standards_combobox_changed)
        self.cable_combobox.addItems(self.cable_mapping.keys())
        self.cable_combobox.currentTextChanged.connect(self.cable_combobox_changed)
        self.combobox_layout.addWidget(self.standards_combobox)
        self.combobox_layout.addWidget(self.cable_combobox)
        self.combobox_widget.setLayout(self.combobox_layout)
        self.form_layout.addRow(self.combobox_widget)

        # Create 8 number inputs using QSpinBox
        self.parameter_labels: List[Parameters] = [
            {"label" : "Rise time [ns]", "arg": "rise_time", "type" : "float", "default": 0.1,
             "min": 0.01, "max": 100},
            {"label" : "Signal width [ns]", "arg": "on_time", "type" : "float", "default": 1,
             "min": 0.05, "max": 100},
            {"label" : "Voltage offset [V]", "arg": "voltage_offset", "type" : "int", "default": 0, "min": 0, "max": 60},
            {"label" : "Length [m]", "arg": "length", "type" : "int", "default": 2, "min": 0, "max": 100},
            {"label" : "Characteristic impedance [Ohm]", "arg": "characteristic_impedance", "type" : "int", "default": 100, "min": 50, "max": 100},
            {"label" : "Skin effect loss constant", "arg": "k1", "type" : "float", "default": 0, "min": 0, "max": 10},
            {"label" : "Vibration/material loss constant", "arg": "k2", "type" : "float", "default": 0, "min": 0, "max": 1},
            {"label" : "Shield loss constant", "arg": "k3", "type" : "float", "default": 0, "min": 0, "max": 5},
        ]
        self.number_inputs: Dict[str, Union[QDoubleSpinBox, QSpinBox]] = {}
        for i, parameter in enumerate(self.parameter_labels):
            arg = parameter["arg"]
            if parameter["type"] == "float":
                self.number_inputs[arg] = DoubleSpinBoxNoWheel()
                self.number_inputs[arg].setMaximum(parameter["max"]) # type: ignore
                self.number_inputs[arg].setMinimum(parameter["min"]) # type: ignore
                self.number_inputs[arg].setDecimals(3)
            elif parameter["type"] == "int":
                self.number_inputs[arg] = SpinBoxNoWheel()
                self.number_inputs[arg].setMaximum(int(parameter["max"]))
                self.number_inputs[arg].setMinimum(int(parameter["min"]))
            self.number_inputs[arg].setValue(parameter['default']) # type: ignore
            self.form_layout.addRow(parameter['label'], self.number_inputs[arg])

        self.standards_combobox_changed(self.standards_combobox.currentText())
        self.cable_combobox_changed(self.cable_combobox.currentText())

        self.frame_layout = QVBoxLayout(self)
        self.frame_layout.addWidget(self.form)

        print(f"Created SimulationFormWidget, label = {label}")

    def delete(self):
        print("Deleting form...")
        self.setParent(None)

    def standards_combobox_changed(self, new_text: str):
        new_standard = self.standards_mapping[new_text]
        self.number_inputs["rise_time"].setValue(new_standard.rise_time) # type: ignore
        self.number_inputs["on_time"].setValue(new_standard.on_time) # type: ignore

    def cable_combobox_changed(self, new_text: str):
        new_cable = self.cable_mapping[new_text]
        self.number_inputs["k1"].setValue(new_cable.k1) # type: ignore
        self.number_inputs["k2"].setValue(new_cable.k2) # type: ignore
        self.number_inputs["k3"].setValue(new_cable.k3) # type: ignore

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

        self.plot_labels: List[str] = []
        self.simulation: Optional[PairSimulation] = None
        self.thread: QThread = QThread(self)
        self.simulations: List[Tuple[TransientAnalysis, float]] = []
        self._display_params: List[SimulationDisplay] = []
        self.plots: Dict[SimulationDisplay, bool] = {}

    def set_display_params(self, display_params: List[SimulationDisplay]):
        self._display_params = display_params
        self._draw_plot()

    def _add_simulation(self, analysis: TransientAnalysis, transmission_delay: float, index: str):
        self.simulations.append((analysis, transmission_delay))
        self.plot_labels.append(index)
        print(f"Draw simulation: {index}")
        self._draw_add(self.simulations[-1], int(self.plot_labels[-1]))

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
                plot_x = self._get_vin_x(analysis, transmission_delay)
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
        for index, simulation in zip(self.plot_labels, self.simulations):
            self._draw_add(simulation, int(index))

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
        self.plot_labels.clear()
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
