import sys
from typing import Literal, TypedDict, Union, cast
from PySpice.Spice.NgSpice.Shared import NgSpiceCommandError
from attr import define

from PyQt5.QtCore import QObject, QThread, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import (QMessageBox, QApplication, QMainWindow,
                             QWidget,QPushButton, QLineEdit, QTextEdit,
                             QVBoxLayout, QHBoxLayout, QFormLayout,
                             QDockWidget, QTabWidget, QScrollArea,
                             QLabel, QSpinBox, QRadioButton, QFrame,
                             QDoubleSpinBox
                             )


import matplotlib
from matplotlib.axes import Axes
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.ticker import EngFormatter

from PySpice.Probe.WaveForm import TransientAnalysis, WaveForm

import numpy

from phyether.dac import DAC
from phyether.ethernet_cable import EthernetCable

from phyether.util import DictMapping, iterable_to_string, string_to_list
from phyether.reed_solomon import RS_Original

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
    presimulation_ratio: int = 0
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
        cable = EthernetCable(**self.init_args)
        pair_input: dict[str, list[int]] = {}
        for pair in ['A', 'B', 'C', 'D']:
            pair_input[pair] = [int(symbol)
                                for symbol in self.input.split()
                                if symbol.removeprefix('-').isdecimal()]

        try:
            analysis = cable.simulate(
                (pair_input['A'], pair_input['A'],
                pair_input['A'], pair_input['A']),
                presimulation_ratio=0, voltage_offset=0
                )
            self.simulation_signal.emit(analysis, cable.transmission_delay)
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
                self.number_inputs[arg] = QDoubleSpinBox()
            elif parameter["type"] == "int":
                self.number_inputs[arg] = QSpinBox()
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
        v_in: WaveForm = analysis['A_vin+'] - analysis['A_vin-']
        v_out: WaveForm = analysis['A_vout+'] - analysis['A_vout-']

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
        self.thread.exit()

    def simulation_error(self):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setText("There was error during simulation, change parameters")
        msg_box.setWindowTitle("Error")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
        self.thread.exit()

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

class EthernetGuiApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()
        self.input_message = ""
        self.output_message = ""
        self.rs = RS_Original(192, 186)
        self.conversion_state: Literal["text", "bytes"] = "text"
        self.tabs = [QWidget() for i in range(4)]
        self.tp_simulation_forms = [SimulationFormWidget("Simulation parameters", 1)]

    def init_ui(self):
        self.setWindowTitle("Simple Encoder/Decoder")
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        self.main_layout = QVBoxLayout(central_widget)
        self.change_tab(0)

    def clear_main_layout(self, index=0):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)

        self.tabs = [QWidget() for i in range(4)]
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.tabs[0], "Reed-Solomon")
        self.tab_widget.addTab(self.tabs[1], "PAM16")
        self.tab_widget.addTab(self.tabs[2], "PAM")
        self.tab_widget.addTab(self.tabs[3], "Twisted-pair simulation")

        self.content_layout = QVBoxLayout(self.tabs[index])
        self.tab_widget.setCurrentIndex(index)
        self.tab_widget.currentChanged.connect(self.change_tab)
        self.main_layout.addWidget(self.tab_widget)

    def change_tab(self, index):
        print("Changed tab:", index)
        self.clear_main_layout(index)
        if index == 0:
            self.init_reed_solomon()
        elif index == 1:
            self.init_pam16()
        elif index == 2:
            self.init_pam()
        elif index == 3:
            self.init_twisted_pair()

    def init_reed_solomon(self):
        top_layout = QHBoxLayout()
        input_form = QFormLayout()
        self.input_text_field = QTextEdit()
        input_form.addRow("Input:", self.input_text_field)

        # Center - buttons
        button_layout = QVBoxLayout()
        self.encode_button = QPushButton("Encode")
        self.convert_button = QPushButton("Convert text -> bytes")
        self.decode_button = QPushButton("Decode")
        button_layout.addWidget(self.encode_button)
        button_layout.addSpacing(-75)
        button_layout.addWidget(self.convert_button)
        button_layout.addSpacing(-75)
        button_layout.addWidget(self.decode_button)

        # Right side - output
        self.output_text_field = QTextEdit()

        top_layout.addLayout(input_form)
        top_layout.addLayout(button_layout)
        top_layout.addWidget(self.output_text_field)

        # Buttons
        self.encode_button.clicked.connect(self.encode)
        self.convert_button.clicked.connect(self.convert)
        self.decode_button.clicked.connect(self.decode)

        # Add the top layout and the new widget to the main layout
        self.content_layout.addLayout(top_layout)

    def init_pam16(self):
        self.pam_input_field = QLineEdit()
        pam16_form = QFormLayout()
        pam16_form.addRow("PAM16 parameters:", self.pam_input_field)

    def init_pam(self):
        pass

    def init_twisted_pair(self):
        self.tp_simulation_forms = [SimulationFormWidget("Simulation parameters", 1)]
        self.tp_scroll_area = QScrollArea()
        self.tp_scroll_area.setWidgetResizable(True)

        # Create a widget to hold your simulation parameters
        self.tp_params_widget = QWidget()
        self.tp_simulation_form = QFormLayout(self.tp_params_widget)

        self.tp_add_button = QPushButton("Add")
        self.tp_simulation_form.addWidget(self.tp_add_button)
        self.tp_add_button.clicked.connect(self.add_simulation_form)

        for i, sim_form in enumerate(self.tp_simulation_forms):
            self.tp_simulation_form.insertRow(i, sim_form)

        # Set the widget for the scroll area
        self.tp_scroll_area.setWidget(self.tp_params_widget)

        # Add the scroll area to the content layout
        self.content_layout.addWidget(self.tp_scroll_area)

        self.simulator_signals = QLineEdit()
        self.content_layout.addWidget(QLabel(f"Twisted pair signals"))
        self.content_layout.addWidget(self.simulator_signals)

        self.tp_simulate_button = QPushButton("Simulate")
        self.content_layout.addWidget(self.tp_simulate_button)
        self.tp_simulate_button.clicked.connect(self.simulate)

        # Add your canvas
        self.tp_canvas = SimulatorCanvas()
        self.content_layout.addWidget(self.tp_canvas)

    def add_simulation_form(self):
        index = len(self.tp_simulation_forms)
        self.tp_simulation_forms.append(SimulationFormWidget("Simulation parameters", index + 1))
        self.tp_simulation_form.insertRow(index, self.tp_simulation_forms[-1])

        # self.tp_simulation_form.insertRow(input_index - 1, f"{input_index}. simulation parameters:", self.tp_simulation_forms[-1])

    def simulate(self):
        print("Simulating...")
        self.tp_canvas.clear_plot()
        for i, form in enumerate(self.tp_simulation_forms):
            args = {key: val.value() for key, val in form.number_inputs.items() }
            try:
                init = SimulationInitArgs(dac=DAC(1, 2, 15),
                                          transmission_type="lossy",
                                          output_impedance=args["output_impedance"],
                                          length=args["length"], # type: ignore
                                          resistance=args["resistance"],
                                          inductance=args["inductance"],
                                          capacitance=args["capacitance"])

                self.tp_canvas.simulate(self.simulator_signals.text(), i + 1, init,
                    SimulationRunArgs(presimulation_ratio=0, voltage_offset=args["voltage_offset"]) # type: ignore
                )
            except Exception as ex:
                self.create_msg_box(f"Simulation failed: {ex}", "Simulation error!")

    def create_msg_box(self, text, title):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setText(text)
        msg_box.setWindowTitle(title)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    def convert(self):
        if self.conversion_state == "text":
            self.conversion_state = "bytes"
            self.convert_button.setText("Convert bytes -> text")
            list_of_bytes = string_to_list(self.input_text_field.toPlainText())
            self.input_text_field.setPlainText(self._list_to_string(list_of_bytes))

            list_of_bytes = string_to_list(self.output_text_field.toPlainText())
            self.output_text_field.setPlainText(self._list_to_string(list_of_bytes))
        else:
            try:
                input_bytes = self._list_from_string(self.input_text_field.toPlainText())
                output_bytes = self._list_from_string(self.output_text_field.toPlainText())
                input_string = iterable_to_string(input_bytes)
                output_string = iterable_to_string(output_bytes)
                self.input_text_field.setPlainText(input_string)
                self.output_text_field.setPlainText(output_string)
                self.conversion_state = "text"
                self.convert_button.setText("Convert text -> bytes")
            except ValueError as ex:
                print(ex)
                self.create_msg_box(
                    f"Couldn't convert byte to text!: {ex}",
                    "conversion error")

    def _list_from_string(self, string):
        """convert str: "0 2 34 20..." to list[int]: [0, 2, 34, 20...]

        :param string: string to convert
        """
        return [int(x) for x in string.split()]

    def _list_to_string(self, list_to_convert):
        return ' '.join(str(x) for x in list_to_convert)

    # Encode using Reed-Solomon
    def encode(self):
        input_text = self.input_text_field.toPlainText()
        print(f"input_text: {input_text}")
        try:
            encoded_text: Union[str, list[int]]
            if self.conversion_state == "text":
                encoded_text = self.rs.encode(input_text)
                self.output_text_field.setPlainText(encoded_text)
            else:
                encoded_text = self.rs.encode(self._list_from_string(input_text))
                self.output_text_field.setPlainText(self._list_to_string(encoded_text))
            print(f"Encoded message: {self.output_text_field.toPlainText()}")
        except Exception as ex:
            self.create_msg_box(f"Couldn't encode: {ex}", "Encoding error!")

    def decode(self):
        if self.conversion_state == "text":
            input_text: Union[str, list[int]] = self.output_text_field.toPlainText()
        else:
            try:
                input_text = self._list_from_string(self.output_text_field.toPlainText())
            except ValueError as ex:
                self.create_msg_box(f"Couldn't convert bytes!: {ex}", "Conversion error!")
                return

        print(f"Decoding message {input_text}")
        try:
            decoded_text, errors = self.rs.decode(input_text)
            print(f"Decoded message: {decoded_text}")
            if isinstance(decoded_text, str):
                self.input_text_field.setPlainText(decoded_text)
            else:
                self.input_text_field.setPlainText(self._list_to_string(decoded_text))
            if errors == -1:
                msg_box_message = "Message couldn't be decoded!"
            else:
                msg_box_message = f"Message decoded, fixed {errors} errors."
            self.create_msg_box(msg_box_message, 'Decode info')
        except ValueError as ex:
            self.create_msg_box(f"Couldn't decode!: {ex}", "Decoding error!")


def main():
    app = QApplication(sys.argv)
    window = EthernetGuiApp()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
