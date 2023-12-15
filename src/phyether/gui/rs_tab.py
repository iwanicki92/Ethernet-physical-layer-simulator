import itertools
import math

from enum import Enum, auto
from traceback import print_exc
from typing import Optional, Protocol, Union, cast, List, Tuple, Dict

from PyQt5.QtCore import (pyqtSlot, pyqtSignal, QObject,
                          QThread, QWaitCondition, QMutex)
from PyQt5.QtGui import QValidator
from PyQt5.QtWidgets import QWidget, QAbstractButton, QLineEdit

from attr import define

from phyether.gui.ui.rs_widget import Ui_RS_Form
from phyether.gui.util import create_msg_box
from phyether.gui.validators import BinListValidator, HexListValidator, IntListValidator
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

@define(slots=False)
class ReedSolomonParams(DictMapping):
    n: int = 192
    k: int = 186
    gf_power: int = 8

@define(kw_only=True, slots=False)
class ReedSolomonArgs(DictMapping):
    n: int = 192
    k: int = 186
    gf: int = 256
    systematic: bool = True
    bch: bool = True
    force: bool = False

class Conversion(Protocol):
    def __call__(self, line_edit: QLineEdit, *max_bits: int) -> None:
        ...

class Converters:
    @staticmethod
    def _text_to_dec(line_edit: QLineEdit, *args) -> None:
        list_of_bytes = string_to_list(line_edit.text())
        line_edit.setText(list_to_string(list_of_bytes))

    @staticmethod
    def _hex_to_dec(line_edit: QLineEdit, *args):
        line_hex = line_edit.text()
        line_edit.setText(' '.join(
            [str(int(hex_num, 16)) for hex_num in line_hex.split()])
            )

    @staticmethod
    def _bin_to_dec(line_edit: QLineEdit, *args):
        line_bin = line_edit.text()
        line_edit.setText(' '.join(
            [str(int(bin_num, 2)) for bin_num in line_bin.split()])
            )

    @staticmethod
    def _dec_to_text(line_edit: QLineEdit, *args):
        line_bytes = list_from_string(line_edit.text())
        line_string = iterable_to_string(line_bytes)
        line_edit.setText(line_string)

    @staticmethod
    def _dec_to_hex(line_edit: QLineEdit, max_bits: int = 8, *args):
        line_bytes = list_from_string(line_edit.text())
        line_edit.setText(' '.join([f'{dec:0{math.ceil(max_bits/4)}x}' for dec in line_bytes]))

    @staticmethod
    def _dec_to_bin(line_edit: QLineEdit, max_bits: int = 8, *args):
        line_bytes = list_from_string(line_edit.text())
        line_edit.setText(' '.join([f'{dec:0{max_bits}b}' for dec in line_bytes]))

encode_decode_converters = {
    Format.TEXT: (lambda x, _ = None: x, lambda x, _ = None: x),
    Format.DEC: (lambda x, _ = None: list_from_string(x), lambda x, _ = None: list_to_string(x)),
    Format.HEX: (lambda x, _ = None: list_from_string(x, 16), lambda x, bits = None: list_to_string(x, 16, math.ceil(bits/4))),
    Format.BIN: (lambda x, _ = None,: list_from_string(x, 2),
                 lambda x, max_bits = 0: ' '.join(
                     [binary.rjust(max_bits, "0") for binary in list_to_string(x, 2).split()])),
}

qline_converters: Dict[Tuple[Format, Format], List[Conversion]] = {
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
    encoded_signal = pyqtSignal(str)
    # encoded message with errors
    encoded_with_errors_signal = pyqtSignal(str)
    # decoded message, errors found, were errors fixed
    decoded_signal = pyqtSignal(str, int, bool)
    # error message and title
    error_signal = pyqtSignal(str, str)
    # detected errors
    detected_signal = pyqtSignal(bool)

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
        self.detect = False
        self.decode = False

    def update(self, rs_args: ReedSolomonArgs, format: Format,
               message_input: str, error_input: str, detect_only: bool, decode_only: bool = False):
        self.rs_args = rs_args
        self.format = format
        self.message_input = message_input
        self.error_input = error_input
        self.detect = detect_only
        self.decode = decode_only
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
            if self.decode:
                encoded = encode_decode_converters[self.format][0](self.message_input)
            else:
                encoded = self._encode(reed_solomon)

            errors = encode_decode_converters[self.format][0](self.error_input)
            if self.format != Format.TEXT:
                resized_errors = itertools.chain(errors, itertools.repeat(0))
                encoded_err: Union[str, List[int]]
                encoded_err = [enc ^ err for enc, err in zip(encoded, resized_errors)]
            else:
                list_encoded = string_to_list(encoded)
                resized_errors = itertools.chain(string_to_list(errors), itertools.repeat(0))
                tmp_encoded = [
                    enc ^ err for enc, err in zip(list_encoded, resized_errors)
                    ]
                encoded_err = iterable_to_string(tmp_encoded)
            if not self.decode:
                self.encoded_signal.emit(encode_decode_converters[self.format][1](encoded, reed_solomon.gf.degree))
            self.encoded_with_errors_signal.emit(
                encode_decode_converters[self.format][1](encoded_err, reed_solomon.gf.degree))
            if self.detect:
                self._detect(encoded_err, reed_solomon)
            else:
                self._decode(encoded_err, reed_solomon)
        except _EncodingException as ex:
            self.error_signal.emit(f"Couldn't encode!: {ex}", "Encoding error!")
        except _DecodingException as ex:
            self.error_signal.emit(f"Couldn't decode!: {ex}", "Decoding error!")
        except Exception as ex:
            print_exc()
            self.error_signal.emit(f"Error with RS arguments!: {ex}", "Error")

    def _detect(self, encoded: Union[str, List[int]], reed_solomon: RS_Original):
        print(f"Detecting errors in: {encoded}")
        try:
            detected = reed_solomon.detect(encoded)
            self.detected_signal.emit(detected)
        except Exception as ex:
            print_exc()
            raise _DecodingException(ex) from ex

    def _encode(self, reed_solomon: RS_Original):
        print(f"Encoding message")
        input = encode_decode_converters[self.format][0](self.message_input)
        try:
            encoded = reed_solomon.encode(input, not self.rs_args.bch)
            return encoded
        except Exception as ex:
            print_exc()
            raise _EncodingException(ex) from ex

    def _decode(self, encoded: Union[str, List[int]],
                reed_solomon: RS_Original):
        try:
            decoded_message, errors, fixed = reed_solomon.decode(encoded,
                                                                 not self.rs_args.bch,
                                                                 self.rs_args.force)
            decoded_message = decoded_message[-len(self.message_input):]
            decoded = cast(str, encode_decode_converters[self.format][1](
                decoded_message, reed_solomon.gf.degree))
            self.decoded_signal.emit(decoded, errors, fixed)
        except Exception as ex:
            print_exc()
            raise _DecodingException(ex) from ex


class RSTab(QWidget, Ui_RS_Form):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self.current_format = Format.TEXT

        self.rs_param_mapping: Dict[str, ReedSolomonParams] = {
            "RS(192,186,256) - 25/40GBASE-T": ReedSolomonParams(192, 186, 8),
            "RS(360,326,1024) - 2.5/5/10GBASE-T1": ReedSolomonParams(360, 326, 10),
        }
        self.standardsComboBox.addItems(self.rs_param_mapping.keys())

        # validators for different format and max input size
        self.validators: Dict[Format, QValidator] = {
            Format.TEXT: NoValidation(self),
            Format.DEC: IntListValidator(
                max = 2**self.rs_gf_spinBox.value() - 1, max_items = self.rs_n_spinBox.value()),
            Format.HEX: HexListValidator(2**self.rs_gf_spinBox.value() - 1, self.rs_n_spinBox.value()),
            Format.BIN: BinListValidator(self.rs_gf_spinBox.value(), self.rs_n_spinBox.value())
            }

        self.update_validators()

        bch = self.bch_checkBox.isChecked()
        self.encoding_worker = EncodingWorker(
            rs_args=ReedSolomonArgs(
                n=self.rs_n_spinBox.value(),
                k=self.rs_k_spinBox.value(),
                gf=2**self.rs_gf_spinBox.value(),
                systematic=self.systematic_checkBox.isChecked(),
                bch=bch,
                force=self.force_checkBox.isChecked() if not bch else False
                ),
            format=self.get_format(),
            message_input=self.input_lineEdit.text(),
            error_input=self.errors_lineEdit.text())

        self.worker_thread = QThread(self)
        self.encoding_worker.encoded_signal.connect(self._encoded)
        self.encoding_worker.encoded_with_errors_signal.connect(self._encoded_errors)
        self.encoding_worker.decoded_signal.connect(self._decoded)
        self.encoding_worker.detected_signal.connect(self._detected)
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
        validator = self.validators[self.get_format()]
        self.input_lineEdit.setValidator(validator)
        self.errors_lineEdit.setValidator(validator)
        self.encoded_lineEdit.setValidator(validator)
        self.encoded_err_lineEdit.setValidator(validator)
        self.decoded_lineEdit.setValidator(validator)
        self.input_lineEdit.setText(validator.fixup(self.input_lineEdit.text()))
        self.errors_lineEdit.setText(validator.fixup(self.errors_lineEdit.text()))
        self.encoded_lineEdit.setText(validator.fixup(self.encoded_lineEdit.text()))
        self.encoded_err_lineEdit.setText(validator.fixup(self.encoded_err_lineEdit.text()))
        self.decoded_lineEdit.setText(validator.fixup(self.decoded_lineEdit.text()))

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
        self.detect_errors_pushButton.setEnabled(state and self.systematic_checkBox.isChecked())

    @pyqtSlot(bool)
    def systematic_changed(self, state):
        self.detect_errors_pushButton.setEnabled(state and self.bch_checkBox.isChecked())

    @pyqtSlot(int)
    def gf_changed(self, value):
        if value != 8:
            if self.text_radioButton.isChecked():
                self.hex_radioButton.setChecked(True)
                self.convert()
            self.text_radioButton.setCheckable(False)
            self.text_radioButton.setEnabled(False)
        else:
            self.text_radioButton.setCheckable(True)
            self.text_radioButton.setEnabled(True)
        self.validators[Format.DEC].max = 2**value - 1  # type: ignore
        self.validators[Format.HEX].max = 2**value - 1  # type: ignore
        self.validators[Format.BIN].max = value  # type: ignore
        self.rs_n_spinBox.setMaximum(2**value - 1)
        self.rs_k_spinBox.setMaximum(2**value - 2)

        # clearing inputs
        self.input_lineEdit.setText("")
        self.errors_lineEdit.setText("")
        self.update_validators()

    @pyqtSlot(int)
    def n_changed(self, value):
        self.validators[Format.DEC].max_items = value  # type: ignore
        self.validators[Format.HEX].max_items = value  # type: ignore
        self.validators[Format.BIN].max_items = value  # type: ignore

    @pyqtSlot(str)
    def comboBoxChanged(self, new_text: str):
        new_params = self.rs_param_mapping[new_text]
        self.rs_n_spinBox.setValue(new_params.n)
        self.rs_k_spinBox.setValue(new_params.k)
        self.rs_gf_spinBox.setValue(new_params.gf_power)

    def _decode_only(self, message):
        self._toggle_enabled(False)
        bch=self.bch_checkBox.isChecked()
        self.encoding_worker.update(
            rs_args=ReedSolomonArgs(
                n=self.rs_n_spinBox.value(),
                k=self.rs_k_spinBox.value(),
                gf=2**self.rs_gf_spinBox.value(),
                systematic=self.systematic_checkBox.isChecked(),
                bch=bch,
                force=self.force_checkBox.isChecked() if not bch else False
                ),
            format=self.get_format(),
            message_input=message,
            error_input=self.errors_lineEdit.text(),
            detect_only=False,
            decode_only=True
            )

    @pyqtSlot()
    def shift_left(self):
        encoded_list: List[str] = self.encoded_lineEdit.text().split()
        if len(encoded_list) == 0:
            return
        encoded = ' '.join(encoded_list[1:] + [encoded_list[0]])
        self.encoded_lineEdit.setText(encoded)
        self._decode_only(encoded)

    @pyqtSlot()
    def shift_right(self):
        encoded_list: List[str] = self.encoded_lineEdit.text().split()
        if len(encoded_list) == 0:
            return
        encoded = ' '.join([encoded_list[-1]] + encoded_list[:-1])
        self.encoded_lineEdit.setText(encoded)
        self._decode_only(encoded)

    def _encode_detect(self, detect_errors: bool):
        self._toggle_enabled(False)
        bch=self.bch_checkBox.isChecked()
        self.encoding_worker.update(
            rs_args=ReedSolomonArgs(
                n=self.rs_n_spinBox.value(),
                k=self.rs_k_spinBox.value(),
                gf=2**self.rs_gf_spinBox.value(),
                systematic=self.systematic_checkBox.isChecked(),
                bch=bch,
                force=self.force_checkBox.isChecked() if not bch else False
                ),
            format=self.get_format(),
            message_input=self.input_lineEdit.text(),
            error_input=self.errors_lineEdit.text(),
            detect_only=detect_errors
            )

    @pyqtSlot()
    def encode(self):
        self._encode_detect(False)

    @pyqtSlot()
    def detect(self):
        self._encode_detect(True)

    def convert(self):
        new_format = self.get_format()
        self.update_validators()
        if self.current_format == new_format:
            return
        line_edits: List[QLineEdit] = [self.input_lineEdit, self.encoded_lineEdit,
                  self.errors_lineEdit, self.encoded_err_lineEdit, self.decoded_lineEdit]

        converter = qline_converters.get((self.current_format, new_format), [])
        try:
            for line_edit in line_edits:
                for converter_func in converter:
                    converter_func(line_edit, self.rs_gf_spinBox.value())
        except Exception as ex:
                print_exc()
                create_msg_box(f"Couldn't convert format!: {ex}",
                               "conversion error")
        self.current_format = new_format

    def _detected(self, detected: bool):
        if detected:
            self.status_lineEdit.setText("Detected errors in codeword")
        else:
            self.status_lineEdit.setText("No errors were detected in codeword")
        self.errors_found_lineEdit.setText("")
        self.worker_thread.exit()
        self._toggle_enabled(True)

    def _encoded(self, encoded: str):
        self.encoded_lineEdit.setText(encoded)

    def _encoded_errors(self, encoded_errors: str):
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
        self.detect_errors_pushButton.setEnabled(busy)
        for button in self.formatButtonGroup.buttons():
            if button != self.text_radioButton or self.rs_gf_spinBox.value() == 8:
                button.setEnabled(busy)

    def _error_msg(self, error: str, title: str):
        create_msg_box(error, title)
        self.worker_thread.exit()
        self._toggle_enabled(True)
