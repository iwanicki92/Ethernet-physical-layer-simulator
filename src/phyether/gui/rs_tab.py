from enum import Enum, auto
import itertools
from traceback import print_exc
from typing import Callable, Union, cast

from PyQt5.QtCore import (pyqtSlot, pyqtSignal, QRegularExpression, QObject,
                          QThread, QWaitCondition, QMutex)
from PyQt5.QtGui import QRegularExpressionValidator, QValidator
from PyQt5.QtWidgets import QWidget, QAbstractButton, QLineEdit

from attr import define

from phyether.gui.ui.rs_widget import Ui_RS_Form
from phyether.gui.util import create_msg_box
from phyether.reed_solomon import RS_Original
from phyether.util import DictMapping, iterable_to_string, list_from_string, list_to_string, string_to_list

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

@define(kw_only=True, slots=False)
class ReedSolomonArgs(DictMapping):
    n: int = 192
    k: int = 186
    gf: int = 256
    systematic: bool = True
    bch: bool = True
    force: bool = False

class Converters:
    @staticmethod
    def _text_to_dec(line_edit: QLineEdit):
        list_of_bytes = string_to_list(line_edit.text())
        line_edit.setText(list_to_string(list_of_bytes))

    @staticmethod
    def _hex_to_dec(line_edit: QLineEdit):
        line_hex = line_edit.text()
        line_edit.setText(' '.join(
            [str(int(hex_num, 16)) for hex_num in line_hex.split()])
            )

    @staticmethod
    def _bin_to_dec(line_edit: QLineEdit):
        line_hex = line_edit.text()
        line_edit.setText(' '.join(
            [str(int(hex_num, 2)) for hex_num in line_hex.split()])
            )

    @staticmethod
    def _dec_to_text(line_edit: QLineEdit):
        line_bytes = list_from_string(line_edit.text())
        line_string = iterable_to_string(line_bytes)
        line_edit.setText(line_string)

    @staticmethod
    def _dec_to_hex(line_edit: QLineEdit):
        line_bytes = list_from_string(line_edit.text())
        line_edit.setText(' '.join([f'{dec:02x}' for dec in line_bytes]))

    @staticmethod
    def _dec_to_bin(line_edit: QLineEdit):
        line_bytes = list_from_string(line_edit.text())
        line_edit.setText(' '.join([f'{dec:08b}' for dec in line_bytes]))

encode_decode_converters = {
    Format.TEXT: (lambda x: x, lambda x: x),
    Format.DEC: (lambda x: list_from_string(x), lambda x: list_to_string(x)),
    Format.HEX: (lambda x: list_from_string(x, 16), lambda x: list_to_string(x, 16)),
    Format.BIN: (lambda x: list_from_string(x, 2), lambda x: list_to_string(x, 2)),
}

qline_converters: dict[tuple[Format, Format], list[Callable[[QLineEdit], None]]] = {
    (Format.TEXT, Format.HEX) : [Converters._text_to_dec, Converters._dec_to_hex],
    (Format.TEXT, Format.DEC) : [Converters._text_to_dec],
    (Format.TEXT, Format.BIN) : [Converters._text_to_dec, Converters._dec_to_bin],
    (Format.DEC, Format.TEXT) : [Converters._dec_to_text],
    (Format.DEC, Format.HEX) : [Converters._dec_to_hex],
    (Format.DEC, Format.BIN) : [Converters._dec_to_bin],
    (Format.HEX, Format.TEXT) : [Converters._hex_to_dec, Converters._dec_to_text],
    (Format.HEX, Format.DEC) : [Converters._hex_to_dec],
    (Format.HEX, Format.BIN) : [Converters._hex_to_dec, Converters._dec_to_bin],
    (Format.BIN, Format.TEXT) : [Converters._bin_to_dec, Converters._dec_to_text],
    (Format.BIN, Format.HEX) : [Converters._bin_to_dec, Converters._dec_to_hex],
    (Format.BIN, Format.DEC) : [Converters._bin_to_dec],
}

class EncodingWorker(QObject):
    # encoded message + encoded with errors
    encoded_signal = pyqtSignal(str, str)
    # decoded message, errors found, were errors fixed
    decoded_signal = pyqtSignal(str, int, bool)
    # error message and title
    error_signal = pyqtSignal(str, str)

    def __init__(self, rs_args: ReedSolomonArgs, format: Format,
                 message_input: str, error_input: str) -> None:
        super().__init__()

        self.rs_args = rs_args
        self.format = format
        self.message_input = message_input
        self.error_input = error_input
        self.wait_condition = QWaitCondition()
        self.mutex = QMutex()
        self.stop = False

    def update(self, rs_args: ReedSolomonArgs, format: Format,
               message_input: str, error_input: str):
        self.rs_args = rs_args
        self.format = format
        self.message_input = message_input
        self.error_input = error_input
        self.wait_condition.wakeOne()

    @pyqtSlot()
    def run(self):
        while True:
            self.mutex.lock()
            if self.stop == True:
                self.mutex.unlock()
                return
            self.wait_condition.wait(self.mutex)
            if self.stop == True:
                self.mutex.unlock()
                return
            else:
                self.encode()
            self.mutex.unlock()

    def encode(self):
        print("Encoding/decoding...")
        try:
            reed_solomon = RS_Original(self.rs_args.n, self.rs_args.k,
                                       self.rs_args.gf, self.rs_args.systematic)
            encoded = self._encode(reed_solomon)
            errors = encode_decode_converters[self.format][0](self.error_input)
            if self.format != Format.TEXT:
                resized_errors = itertools.chain(errors, itertools.repeat(0))
                encoded_err: Union[str, list[int]]
                encoded_err = [enc ^ err for enc, err in zip(encoded, resized_errors)]
            else:
                list_encoded = string_to_list(encoded)
                resized_errors = itertools.chain(string_to_list(errors), itertools.repeat(0))
                tmp_encoded = [
                    enc ^ err for enc, err in zip(list_encoded, resized_errors)
                    ]
                encoded_err = iterable_to_string(tmp_encoded)
            self.encoded_signal.emit(
                encode_decode_converters[self.format][1](encoded),
                encode_decode_converters[self.format][1](encoded_err)
                )
            self._decode(encoded_err, reed_solomon)
        except _EncodingException as ex:
            self.error_signal.emit(f"Couldn't encode!: {ex}", "Encoding error!")
        except _DecodingException as ex:
            self.error_signal.emit(f"Couldn't decode!: {ex}", "Decoding error!")
        except Exception as ex:
            print_exc()
            self.error_signal.emit(f"Error with RS arguments!: {ex}", "Error")

    def _encode(self, reed_solomon: RS_Original):
        print(f"Encoding message")
        input = encode_decode_converters[self.format][0](self.message_input)
        try:
            encoded = reed_solomon.encode(input, not self.rs_args.bch)
            print(f"{encoded=}")
            return encoded
        except Exception as ex:
            print_exc()
            raise _EncodingException(ex) from ex

    def _decode(self, encoded: Union[str, list[int]],
                reed_solomon: RS_Original):
        print(f"Decoding message {encoded}")
        try:
            decoded_message, errors, fixed = reed_solomon.decode(encoded,
                                                                 not self.rs_args.bch,
                                                                 self.rs_args.force)
            decoded_message = decoded_message[-len(self.message_input):]
            print(f'{len(self.message_input)=}')
            decoded = cast(str, encode_decode_converters[self.format][1](decoded_message))
            self.decoded_signal.emit(decoded, errors, fixed)
            print(f"Decoded message: {decoded_message=}")
        except Exception as ex:
            print_exc()
            raise _DecodingException(ex) from ex


class RSTab(QWidget, Ui_RS_Form):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self.current_format = Format.TEXT

        # "^pattern(\s+pattern)*\s?" pattern rozdzielony spacjami mogący się kończyć spacją
        dec_regex = QRegularExpression(r"^(2[0-4][0-9]|25[0-5]|[0-1][0-9]{1,2}|[0-9]{1,2})(\s+(2[0-4][0-9]|25[0-5]|[0-1][0-9]{1,2}|[0-9]{1,2}))*\s?")
        hex_regex = QRegularExpression(r"^[[:xdigit:]]{2}(\s+[[:xdigit:]]{2})*\s?")
        bin_regex = QRegularExpression(r"^[01]{8}(\s+[01]{8})*\s?")

        # validators for different format and max input size
        self.validators: dict[Format, tuple[QValidator, int]] = {
            Format.TEXT: (NoValidation(self), 256),
            Format.DEC: (QRegularExpressionValidator(dec_regex, self), 256 * 4),
            Format.HEX: (QRegularExpressionValidator(hex_regex, self), 256 * 3),
            Format.BIN: (QRegularExpressionValidator(bin_regex, self), 256 * 9)
            }

        self.update_validators()

        bch = self.bch_checkBox.isChecked()
        self.encoding_worker = EncodingWorker(
            rs_args=ReedSolomonArgs(
                n=self.rs_n_spinBox.value(),
                k=self.rs_k_spinBox.value(),
                gf=self.rs_gf_spinBox.value(),
                systematic=self.systematic_checkBox.isChecked(),
                bch=bch,
                force=self.force_checkBox.isChecked() if not bch else False
                ),
            format=self.get_format(),
            message_input=self.input_lineEdit.text(),
            error_input=self.errors_lineEdit.text())

        self.worker_thread = QThread(self)
        self.encoding_worker.encoded_signal.connect(self._encoded)
        self.encoding_worker.decoded_signal.connect(self._decoded)
        self.encoding_worker.error_signal.connect(self._error_msg)
        self.encoding_worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.encoding_worker.run) # type: ignore
        self.worker_thread.start()

    def on_close(self):
        self.encoding_worker.mutex.lock()
        self.encoding_worker.stop = True
        self.encoding_worker.mutex.unlock()
        self.encoding_worker.wait_condition.wakeAll()
        self.worker_thread.exit()
        self.worker_thread.wait()

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
        self._toggle_enabled(False)
        bch=self.bch_checkBox.isChecked()
        self.encoding_worker.update(
            rs_args=ReedSolomonArgs(
                n=self.rs_n_spinBox.value(),
                k=self.rs_k_spinBox.value(),
                gf=self.rs_gf_spinBox.value(),
                systematic=self.systematic_checkBox.isChecked(),
                bch=bch,
                force=self.force_checkBox.isChecked() if not bch else False
                ),
            format=self.get_format(),
            message_input=self.input_lineEdit.text(),
            error_input=self.errors_lineEdit.text())

    def convert(self):
        new_format = self.get_format()
        self.update_validators()
        if self.current_format == new_format:
            return
        line_edits: list[QLineEdit] = [self.input_lineEdit, self.encoded_lineEdit,
                  self.errors_lineEdit, self.encoded_err_lineEdit, self.decoded_lineEdit]

        converter = qline_converters.get((self.current_format, new_format), [])
        try:
            for line_edit in line_edits:
                for converter_func in converter:
                    converter_func(line_edit)
        except Exception as ex:
                print_exc()
                create_msg_box(f"Couldn't convert format!: {ex}",
                               "conversion error")
        self.current_format = new_format

    def _encoded(self, encoded: str, encoded_errors: str):
        self.encoded_lineEdit.setText(encoded)
        self.encoded_err_lineEdit.setText(encoded_errors)

    def _decoded(self, decoded: str, errors: int, fixed: bool):
        self.decoded_lineEdit.setText(decoded)
        if fixed:
            self.status_lineEdit.setText(f"Message decoded")
        else:
            self.status_lineEdit.setText("Message couldn't be decoded!")
        if errors == -1:
            self.errors_found_lineEdit.setText("Too many errors")
        else:
            self.errors_found_lineEdit.setText(str(errors))
        self.worker_thread.exit()
        self._toggle_enabled(True)

    def _toggle_enabled(self, busy: bool):
        self.encode_decode_pushButton.setEnabled(busy)
        for button in self.formatButtonGroup.buttons():
            button.setEnabled(busy)

    def _error_msg(self, error: str, title: str):
        create_msg_box(error, title)
        self.worker_thread.exit()
        self._toggle_enabled(True)
