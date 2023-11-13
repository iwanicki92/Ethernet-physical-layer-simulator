from enum import Enum, auto
from typing import Any, Callable, Optional, Union, cast

from PyQt5.QtCore import pyqtSlot, QRegularExpression
from PyQt5.QtGui import QRegularExpressionValidator, QValidator
from PyQt5.QtWidgets import QWidget, QAbstractButton, QLineEdit

from phyether.gui.ui.rs_widget import Ui_RS_Form
from phyether.gui.util import create_msg_box
from phyether.reed_solomon import RS_Original
from phyether.util import iterable_to_string, list_from_string, list_to_string, string_to_list

class _EncodingException(Exception):
     pass
class _DecodingException(Exception):
     pass

class Format(Enum):
    TEXT = auto()
    HEX = auto()
    DEC = auto()
    BIN = auto()

class NoValidation(QValidator):
    def validate(self, a0: str, a1: int):
        return QValidator.State.Acceptable, a0, a1

class RSTab(QWidget, Ui_RS_Form):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self.current_format = Format.TEXT

        dec_regex = QRegularExpression(r"^(2[0-4][0-9]|25[0-5]|[0-1][0-9]{1,2}|[0-9]{1,2})(\s+(2[0-4][0-9]|25[0-5]|[0-1][0-9]{1,2}|[0-9]{1,2}))*\s?")
        # "^pattern(\s+pattern)*\s?" pattern rozdzielony spacjami mogący się kończyć spacją
        hex_regex = QRegularExpression(r"^[[:xdigit:]]{2}(\s+[[:xdigit:]]{2})*\s?")
        bin_regex = QRegularExpression(r"^[01]{8}(\s+[01]{8})*\s?")

        # validators for different format and max input size
        self.validators: dict[Format, tuple[QValidator, int]] = {
            Format.TEXT: (NoValidation(self), 256),
            Format.DEC: (QRegularExpressionValidator(dec_regex, self), 256 * 4),
            Format.HEX: (QRegularExpressionValidator(hex_regex, self), 256 * 3),
            Format.BIN: (QRegularExpressionValidator(bin_regex, self), 256 * 9)
            }

        self.encode_decode_converters = {
            Format.TEXT: (lambda x: x, lambda x: x),
            Format.DEC: (lambda x: list_from_string(x), lambda x: list_to_string(x)),
            Format.HEX: (lambda x: list_from_string(x, 16), lambda x: list_to_string(x, 16)),
            Format.BIN: (lambda x: list_from_string(x, 2), lambda x: list_to_string(x, 2)),
            }

        self.input_converters: dict[tuple[Format, Format], list[Callable[[QLineEdit], None]]] = {
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

        self.update_validators()

    def update_validators(self):
        validator, size = self.validators[self.get_format()]
        self.input_lineEdit.setValidator(validator)
        self.input_lineEdit.setMaxLength(size)
        self.errors_lineEdit.setValidator(validator)
        self.errors_lineEdit.setMaxLength(size)

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
        input_format = self.get_format()
        try:
             encoded = self._encode(reed_solomon, input_format)
             print(f"{encoded=}")
             self._decode(encoded, reed_solomon, input_format)
        except _EncodingException as ex:
            create_msg_box(f"Couldn't encode!: {ex}", "Encoding error!")
        except _DecodingException as ex:
            create_msg_box(f"Couldn't decode!: {ex}", "Decoding error!")

    def _encode(self, reed_solomon: RS_Original, input_format: Format):
        # TODO: create new RS depending on parameters
        print(f"Encoding message")
        input_text = cast(str, self.input_lineEdit.text())
        input = self.encode_decode_converters[input_format][0](input_text)
        try:
            encoded = reed_solomon.encode(input)
            self.encoded_lineEdit.setText(self.encode_decode_converters[input_format][1](encoded))
        except Exception as ex:
            raise _EncodingException from ex
        return encoded

    def _decode(self, encoded: Union[str, list[int]],
                reed_solomon: RS_Original,
                input_format: Format):
        # TODO: add errors to encoding
        print(f"Decoding message {encoded}")
        try:
            decoded_text, errors = reed_solomon.decode(encoded)
            decoded = cast(str, self.encode_decode_converters[input_format][1](decoded_text))
            self.decoded_lineEdit.setText(decoded)
            print(f"Decoded message: {decoded}")
            if errors == -1:
                self.status_lineEdit.setText("Message couldn't be decoded!")
                self.errors_found_lineEdit.setText("-")
            else:
                self.status_lineEdit.setText(f"Message decoded")
                self.errors_found_lineEdit.setText(str(errors))
        except Exception as ex:
            raise _DecodingException from ex

    def convert(self):
        new_format = self.get_format()
        self.update_validators()
        if self.current_format == new_format:
            return
        line_edits: list[QLineEdit] = [self.input_lineEdit, self.encoded_lineEdit,
                  self.errors_lineEdit, self.decoded_lineEdit]

        converter = self.input_converters.get((self.current_format, new_format), [])
        try:
            for line_edit in line_edits:
                for converter_func in converter:
                    converter_func(line_edit)
        except Exception as ex:
                print(ex)
                create_msg_box(f"Couldn't convert format!: {ex}",
                               "conversion error")
        self.current_format = new_format

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
