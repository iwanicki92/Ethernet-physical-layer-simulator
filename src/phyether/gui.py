import sys
from PyQt6.QtWidgets import QMessageBox, QStyle, QApplication, QMainWindow, QWidget, QPushButton, QLineEdit, QTextEdit, QVBoxLayout, QHBoxLayout, QFormLayout

import numpy as np

from util import iterable_to_string, string_to_list
from reed_solomon import RS_Original, corrupt_message

class EthernetGuiApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()
        self.input_message = ""
        self.output_message = ""
        self.rs = RS_Original(192, 186)

    def init_ui(self):
        self.setWindowTitle("Simple Encoder/Decoder")
        self.setGeometry(100, 100, 600, 300)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Horizontal layout
        main_layout = QHBoxLayout(central_widget)

        # Left side - inputs
        input_form = QFormLayout()
        self.input_text_field = QTextEdit()
        self.input_number_field = QLineEdit()
        input_form.addRow("Input:", self.input_text_field)
        input_form.addRow("Number of errors:", self.input_number_field)
        load_button = QPushButton("Load message")
        input_form.addWidget(load_button)

        # Center - buttons
        button_layout = QVBoxLayout()
        encode_button = QPushButton("Encode")
        switch_button = QPushButton("<--")
        decode_button = QPushButton("Decode")
        button_layout.addWidget(encode_button)
        button_layout.addSpacing(-75)
        button_layout.addWidget(switch_button)
        button_layout.addSpacing(-75)
        button_layout.addWidget(decode_button)

        # Right side - output
        self.output_text_field = QTextEdit()
        self.output_text_field.setReadOnly(True)

        main_layout.addLayout(input_form)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.output_text_field)

        # Connect the buttons to their respective functions
        encode_button.clicked.connect(self.encode)
        switch_button.clicked.connect(self.switch_messages)
        decode_button.clicked.connect(self.decode)
        load_button.clicked.connect(self.load)

    # Set input message to output message and delete output
    def switch_messages(self):
        self.input_message, self.output_message = self.output_message, ""
        self.input_text_field.setPlainText(self.input_message)
        self.output_text_field.setPlainText(self.output_message)

    # Load message from input
    def load(self):
        self.input_message = self.input_text_field.toPlainText()

    # Encode using Reed-Solomon and corrupt
    def encode(self):
        input_text = self.input_message
        try:
            input_number_of_errors = int(self.input_number_field.text())
        except:
            input_number_of_errors = 0
            self.input_number_field.setText("0")

        print(f"input_text: {input_text}, errors: {input_number_of_errors}")

        print(f"Encoding message '{input_text}' with {input_number_of_errors} errors...")
        encoded_text = self.rs.encode(input_text)
        
        if input_number_of_errors:
            print("Corrupting...")
            final_encoded_text = corrupt_message(encoded_text, input_number_of_errors, "beginning")
        else:
            final_encoded_text = encoded_text

        self.output_message = final_encoded_text
        self.output_text_field.setPlainText(final_encoded_text)
        print(f"Encoded message: {self.output_text_field.toPlainText()}")

    # Decode using Berlekamp-Welch
    def decode(self):
        input_text = self.input_message
        
        print(f"Decoding message {input_text}...")
        decoded_text, errors = self.rs.decode(input_text)
        errors = errors if errors != -1 else 0

        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setText(f"Message decoded, fixed {errors} errors.")
        msg_box.setWindowTitle('Decode info')
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        result = msg_box.exec()

        print(f"Decoded message: {decoded_text}")
        self.output_text_field.setPlainText(decoded_text)

def main():
    app = QApplication(sys.argv)
    window = EthernetGuiApp()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
