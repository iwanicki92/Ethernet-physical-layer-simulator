import sys
from typing import Literal, Union
from PyQt5.QtWidgets import (QMessageBox, QApplication, QMainWindow,
                             QWidget,QPushButton, QLineEdit, QTextEdit,
                             QVBoxLayout, QHBoxLayout, QFormLayout)
import matplotlib
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.ticker import EngFormatter

from PySpice.Probe.WaveForm import WaveForm
from phyether.dac import DAC
from phyether.twisted_pair import TwistedPair

from phyether.util import iterable_to_string, string_to_list
from phyether.reed_solomon import RS_Original

matplotlib.use('QtAgg')


class SimulatorCanvas(FigureCanvasQTAgg):
    def __init__(self):
        super().__init__()

        self.pair = TwistedPair(
            dac=DAC(1, 3, 4),
            output_impedance=90,
            length=50,
            resistance=0.5,
            inductance=400,
            capacitance=70,
            transmission_type='lossy'
            )

        self.axes = self.figure.add_subplot(111)
        self.axes.grid(True)
        self.draw()

    def simulate(self, input):
        analysis = self.pair.simulate([
            int(symbol) for symbol in input.split()
            if symbol.removeprefix('-').isdecimal()
            ], 3)
        v_in: WaveForm = analysis['vin+'] - analysis['vin-']
        v_out: WaveForm = analysis['vout+'] - analysis['vout-']

        vx_out_transformed = analysis.time - self.pair.transmission_delay
        vx_out_transformed = vx_out_transformed[vx_out_transformed>=0]
        # trim v_in where nothing happens after shifting v_out
        vx_in_transformed = analysis.time[
            analysis.time<(analysis.time[-1] - self.pair.transmission_delay)
            ]

        self.axes.cla()
        self.axes.plot(
            vx_in_transformed,
            v_in[:len(vx_in_transformed)],
            vx_out_transformed,
            v_out[-len(vx_out_transformed):]
            )
        self.axes.xaxis.set_major_formatter(EngFormatter(unit='s'))

        self.axes.set_xlabel('Time')
        self.axes.set_ylabel('Voltage (V)')
        self.axes.grid(True)
        self.axes.legend(['v(in+, in-)', 'v(out+, out-)'], loc='upper right')
        self.draw()


class EthernetGuiApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()
        self.input_message = ""
        self.output_message = ""
        self.rs = RS_Original(192, 186)
        self.conversion_state: Literal["text", "bytes"] = "text"

    def init_ui(self):
        self.setWindowTitle("Simple Encoder/Decoder")
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Vertical layout to stack elements vertically
        main_layout = QVBoxLayout(central_widget)

        # Top layout for the existing elements (input, buttons, output)
        top_layout = QHBoxLayout()

        # Left side - inputs
        input_form = QFormLayout()
        self.input_text_field = QTextEdit()
        input_form.addRow("Input:", self.input_text_field)

        # Center - buttons
        button_layout = QVBoxLayout()
        encode_button = QPushButton("Encode")
        self.convert_button = QPushButton("Convert text -> bytes")
        decode_button = QPushButton("Decode")
        button_layout.addWidget(encode_button)
        button_layout.addSpacing(-75)
        button_layout.addWidget(self.convert_button)
        button_layout.addSpacing(-75)
        button_layout.addWidget(decode_button)

        # Right side - output
        self.output_text_field = QTextEdit()

        top_layout.addLayout(input_form)
        top_layout.addLayout(button_layout)
        top_layout.addWidget(self.output_text_field)

        # Add the top layout and the new widget to the main layout
        main_layout.addLayout(top_layout)

        # Simulator below
        self.simulation_input_field = QLineEdit()
        simulation_form = QFormLayout()
        simulation_form.addRow("Simulation parameters:", self.simulation_input_field)

        simulate_button = QPushButton("Simulate")
        simulation_form.addWidget(simulate_button)
        simulate_button.clicked.connect(self.simulate)

        self.canvas = SimulatorCanvas()
        main_layout.addWidget(self.canvas)

        main_layout.addLayout(simulation_form)

        # Connect the buttons to their respective functions
        encode_button.clicked.connect(self.encode)
        self.convert_button.clicked.connect(self.convert)
        decode_button.clicked.connect(self.decode)

    def simulate(self):
        print("Simulating...")
        simulator_parameters = self.simulation_input_field.text()
        try:
            self.canvas.simulate(simulator_parameters)
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
