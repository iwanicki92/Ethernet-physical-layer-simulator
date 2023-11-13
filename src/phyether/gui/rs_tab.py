from enum import Enum, auto
from typing import Callable, Optional, Union, cast

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QAbstractButton, QLineEdit

from phyether.gui.ui.rs_widget import Ui_RS_Form
from phyether.gui.util import create_msg_box
from phyether.reed_solomon import RS_Original
from phyether.util import iterable_to_string, list_from_string, list_to_string, string_to_list

class Format(Enum):
    TEXT = auto()
    HEX = auto()
    DEC = auto()
    BIN = auto()

class RSTab(QWidget, Ui_RS_Form):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self.current_format = Format.TEXT
        # TODO: Add validation to input fields

    def get_format(self) -> Format:
        if self.text_radioButton.isChecked():
            return Format.TEXT
        elif self.hex_radioButton.isChecked():
            return Format.HEX
        elif self.dec_radioButton.isChecked():
            return Format.DEC
        else:
            return Format.BIN

    @pyqtSlot(QAbstractButton)
    def format_changed(self, format_radiobutton: QAbstractButton):
        print(format_radiobutton.text())
        self.convert()

    @pyqtSlot(bool)
    def bch_changed(self, state):
        self.force_checkBox.setEnabled(not state)

    @pyqtSlot()
    def encode(self):
        # TODO: encode/decode in another thread
        reed_solomon = RS_Original(192, 186)
        encoded = self._encode(reed_solomon)
        self._decode(encoded, reed_solomon)

    def _encode(self, reed_solomon: RS_Original):
        # TODO: create new RS depending on parameters
        input_text = cast(str, self.input_lineEdit.text())
        print(f"input_text: {input_text}")
        try:
            encoded_text: Union[str, list[int]]
            input_format = self.get_format()
            if input_format == Format.TEXT:
                encoded_text = reed_solomon.encode(input_text)
                self.encoded_lineEdit.setText(encoded_text)
            elif input_format == Format.DEC:
                encoded_text = reed_solomon.encode(list_from_string(input_text))
                self.encoded_lineEdit.setText(list_to_string(encoded_text))
            else:
                encoded_text = "NOT IMPLEMENTED"
            print(f"Encoded message: {encoded_text}")
            return encoded_text
        except Exception as ex:
            create_msg_box(f"Couldn't encode: {ex}", "Encoding error!")
            return ""

    def _decode(self, encoded: Union[str, list[int]], reed_solomon: RS_Original):
        # TODO: add errors to encoding
        print(f"Decoding message {encoded}")
        try:
            decoded_text, errors = reed_solomon.decode(encoded)
            print(f"Decoded message: {decoded_text}")
            if isinstance(decoded_text, str):
                self.decoded_lineEdit.setText(decoded_text)
            else:
                self.decoded_lineEdit.setText(list_to_string(decoded_text))
            if errors == -1:
                self.status_lineEdit.setText("Message couldn't be decoded!")
            else:
                self.status_lineEdit.setText(f"Message decoded")
                self.errors_found_lineEdit.setText(str(errors))
        except ValueError as ex:
            create_msg_box(f"Couldn't decode!: {ex}", "Decoding error!")

    def _text_to_dec(self, line_edit: QLineEdit):
        list_of_bytes = string_to_list(line_edit.text())
        line_edit.setText(list_to_string(list_of_bytes))

    def _hex_to_dec(self, line_edit: QLineEdit):
        line_hex = line_edit.text()
        line_edit.setText(' '.join(
            [str(int(hex_num, 16)) for hex_num in line_hex.split()])
            )

    def _bin_to_dec(self, line_edit: QLineEdit):
        line_hex = line_edit.text()
        line_edit.setText(' '.join(
            [str(int(hex_num, 2)) for hex_num in line_hex.split()])
            )

    def _dec_to_text(self, line_edit: QLineEdit):
        line_bytes = list_from_string(line_edit.text())
        line_string = iterable_to_string(line_bytes)
        line_edit.setText(line_string)

    def _dec_to_hex(self, line_edit: QLineEdit):
        line_bytes = list_from_string(line_edit.text())
        line_edit.setText(' '.join([f'{dec:02x}' for dec in line_bytes]))

    def _dec_to_bin(self, line_edit: QLineEdit):
        line_bytes = list_from_string(line_edit.text())
        line_edit.setText(' '.join([f'{dec:08b}' for dec in line_bytes]))


    def convert(self):
        new_format = self.get_format()
        if self.current_format == new_format:
            return
        line_edits: list[QLineEdit] = [self.input_lineEdit, self.encoded_lineEdit,
                  self.errors_lineEdit, self.decoded_lineEdit]
        converters: dict[tuple[Format, Format], list[Callable[[QLineEdit], None]]] = {
            (Format.TEXT, Format.HEX) : [self._text_to_dec, self._dec_to_hex],
            (Format.TEXT, Format.DEC) : [self._text_to_dec],
            (Format.TEXT, Format.BIN) : [self._text_to_dec, self._dec_to_bin],
            (Format.DEC, Format.TEXT) : [self._dec_to_text],
            (Format.DEC, Format.HEX) : [self._dec_to_hex],
            (Format.DEC, Format.BIN) : [self._dec_to_bin],
            (Format.HEX, Format.TEXT) : [self._hex_to_dec, self._dec_to_text],
            (Format.HEX, Format.DEC) : [self._hex_to_dec],
            (Format.HEX, Format.BIN) : [self._hex_to_dec, self._dec_to_bin],
            (Format.BIN, Format.TEXT) : [self._bin_to_dec, self._dec_to_text],
            (Format.BIN, Format.HEX) : [self._bin_to_dec, self._dec_to_hex],
            (Format.BIN, Format.DEC) : [self._bin_to_dec],
            }
        converter = converters.get((self.current_format, new_format), [])
        try:
            for line_edit in line_edits:
                for converter_func in converter:
                    converter_func(line_edit)
        except Exception as ex:
                print(ex)
                create_msg_box(f"Couldn't convert format!: {ex}",
                               "conversion error")
        self.current_format = new_format
