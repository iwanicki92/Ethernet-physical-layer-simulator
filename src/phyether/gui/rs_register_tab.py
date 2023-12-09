import sys
from pathlib import Path
from typing import Literal, Union

from PyQt5.QtWidgets import QWidget, QLineEdit, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSlot

from phyether.gui.ui.rs_register_widget import Ui_rsRegisterForm

from galois import GF, Poly

from phyether.gui.util import create_msg_box
from phyether.gui.validators import IntListValidator
from phyether.reed_solomon_bch import BCH_RS

class ReedSolomonRegisterArguments:
    def __init__(self, n: int, k: int, gf: int, primitive_poly = None,
                 *, repr: Literal['poly', 'int', 'power'] = 'int') -> None:
        self.n = n
        self.k = k
        self.gf = GF(gf,
                     irreducible_poly=primitive_poly,
                     repr=repr)
        self.generating_poly: Poly = Poly([0], field=self.gf)

    def copy(self):
        return ReedSolomonRegisterArguments(
            self.n, self.k, self.gf.order,
            self.gf.irreducible_poly,
            repr=self.gf.element_repr
            )

class RSRegisterTab(QWidget, Ui_rsRegisterForm):
    def __init__(self) -> None:
        super().__init__()
        self.rs_param_mapping: dict[str, ReedSolomonRegisterArguments] = {
            "RS(192,186,256) - 25/40GBASE-T": ReedSolomonRegisterArguments(192, 186, 2**8, 0x11D),
            "RS(360,326,1024) - 2.5/5/10GBASE-T1": ReedSolomonRegisterArguments(360, 326, 2**10, 0x409),
            "RS(528,514,1024) - 10/25GBASE-R, 100GBASE-(C/K/S)R4": ReedSolomonRegisterArguments(528, 514, 2**10, 0x409),
            "RS(544,514,1024) - 100GBASE-KP4, 100GBASE-(C/K/S)R2": ReedSolomonRegisterArguments(544, 514, 2**10, 0x409),
        }
        self.current_arguments = self.rs_param_mapping["RS(192,186,256) - 25/40GBASE-T"].copy()

        self.setupUi(self)
        self.delay_elements: list[QLineEdit] = []
        current_dir = Path(__file__).parent
        images = current_dir / "../resources/img"
        self.imageLabel: QLabel
        self.imageLabel.setPixmap(QPixmap(str(images / "RS_shift_register.png")))
        self.imageLabel.setScaledContents(True)
        if len(sys.argv) >= 3:
            try:
                self.imageLabel.setMaximumSize(int(sys.argv[1]), int(sys.argv[2]))
            except Exception as ex:
                create_msg_box(f"Couldn't parse arguments: {ex}", "Error")
        self.standardsComboBox.addItems(self.rs_param_mapping.keys())
        self._calculate_gen_poly()
        self.bch = BCH_RS(self.current_arguments.n, self.current_arguments.k, self.current_arguments.gf, self.current_arguments.generating_poly)
        self.update_n_k_max(self.current_arguments.gf.degree)
        self.update_validators()
        self._clear()


    @pyqtSlot(str)
    def comboBoxChanged(self, new_text: str):
        new_params = self.rs_param_mapping[new_text].copy()
        self.current_arguments = new_params
        self.rs_n_spinBox.setValue(new_params.n)
        self.rs_k_spinBox.setValue(new_params.k)
        self.rs_gf_spinBox.setValue(new_params.gf.degree)
        self.rs_primitive_element_lineEdit.setText(str(new_params.gf.primitive_element))
        self.rs_primitive_poly_lineEdit.setText(str(new_params.gf.irreducible_poly))
        self._calculate_gen_poly()
        self.update_validators()

    def update_n_k_max(self, gf_order):
        self.rs_n_spinBox.setMaximum(2**gf_order - 1)
        self.rs_k_spinBox.setMaximum(2**gf_order - 2)

    def update_validators(self):
        field_order = self.current_arguments.gf.order
        self.input_lineEdit.setValidator(IntListValidator(field_order - 1,
                                                          self.rs_k_spinBox.value()))
        self.fill_SpinBox.setMaximum(field_order - 1)

    @pyqtSlot(bool)
    def poly_repr_checked(self, bool):
        poly_or_int: Literal['int', 'poly'] = 'int' if bool else 'poly'
        for params in self.rs_param_mapping.values():
            params.gf.repr(poly_or_int)
        self.current_arguments.gf.repr(poly_or_int)
        self.rs_primitive_element_lineEdit.setText(str(self.current_arguments.gf.primitive_element))
        self.rs_primitive_poly_lineEdit.setText(str(self.current_arguments.gf.irreducible_poly))
        self.gen_poly_lineEdit.setText(str(self.current_arguments.generating_poly))
        self.update_parity()

    @pyqtSlot(int)
    def gf_changed(self, value):
        self.update_n_k_max(value)

    @pyqtSlot()
    def whole_message(self):
        for _ in range(self.bch.n - self.bch.i):
            self._next_symbol()

    @pyqtSlot()
    def calculate_generating_poly(self):
        try:
            self.current_arguments = ReedSolomonRegisterArguments(
                    self.rs_n_spinBox.value(), self.rs_k_spinBox.value(),
                    2**self.rs_gf_spinBox.value(),
                    primitive_poly=self.rs_primitive_poly_lineEdit.text(),
                    repr = "int" if self.poly_repr_checkBox.isChecked() else "poly"
                )
        except Exception as ex:
            create_msg_box(str(ex), "Error")
            return
        self.rs_primitive_element_lineEdit.setText(str(self.current_arguments.gf.primitive_element))
        self._calculate_gen_poly()
        self._clear()
        self.update_validators()

    @pyqtSlot()
    def next_symbol(self):
        try:
            self._next_symbol()
        except Exception as ex:
            create_msg_box(str(ex), "Error")

    def _next_symbol(self):
        symbols = self.input_lineEdit.text().split()
        self.input_lineEdit.setText(' '.join(symbols[1:]))
        output = self.output_lineEdit.text()
        if self.bch.i >= self.current_arguments.k:
            symbol = None
        elif symbols:
            symbol = symbols[0]
        else:
            symbol = str(self.fill_SpinBox.value())
        encoded = self.bch.encode_next_symbol(symbol)
        self.output_lineEdit.setText(output + " " + str(encoded))
        self.update_parity()

    @pyqtSlot()
    def next_x_symbols(self):
        try:
            symbols = min(self.x_symbols_spinBox.value(), self.bch.n - self.bch.i)
            if symbols <= 0:
                create_msg_box("You need to clear encoder before encoding new message", "error")
            for _ in range(min(self.x_symbols_spinBox.value(), self.bch.n - self.bch.i)):
                self._next_symbol()
        except Exception as ex:
            create_msg_box(str(ex), "Error")

    @pyqtSlot()
    def clear(self):
        self._clear()

    def _clear(self):
        self.output_lineEdit.setText("")
        self.bch.clear_parity()
        self.update_parity()

    def update_parity(self):
        for symbol, delay_element in zip(self.bch.parity, reversed(self.delay_elements)):
            delay_element.setText(str(symbol))

    @pyqtSlot()
    def calculate_primitives(self):
        try:
            self.current_arguments = ReedSolomonRegisterArguments(
                self.rs_n_spinBox.value(), self.rs_k_spinBox.value(),
                2**self.rs_gf_spinBox.value(),
                repr = 'int' if self.poly_repr_checkBox.isChecked() else 'poly'
            )
            self.rs_primitive_poly_lineEdit.setText(
                str(self.current_arguments.gf.irreducible_poly))
            self.rs_primitive_element_lineEdit.setText(
                str(self.current_arguments.gf.primitive_element))
            self._calculate_gen_poly()
            self._clear()
            self.update_validators()
        except Exception as ex:
            create_msg_box(f"Error calculating primitives: ", "Error")

    def _calculate_gen_poly(self):
        t = self.current_arguments.n - self.current_arguments.k
        x_poly = Poly.Str('x', self.current_arguments.gf)
        poly = x_poly - self.current_arguments.gf.primitive_element**0 # type: ignore
        for i in range(1, t):
            poly *= x_poly - self.current_arguments.gf.primitive_element**i

        self.current_arguments.generating_poly = poly
        self.bch = BCH_RS(self.current_arguments.n, self.current_arguments.k, self.current_arguments.gf, self.current_arguments.generating_poly)
        self.gen_poly_lineEdit.setText(str(poly))
        self.delay_elements = [QLineEdit() for _ in range(t)]

        for i in reversed(range(self.scroll_horizontalLayout.count())):
            widget = self.scroll_horizontalLayout.itemAt(i).widget()
            self.scroll_horizontalLayout.removeWidget(widget)

        for i, delay_element in enumerate(self.delay_elements):
            self.scroll_horizontalLayout.addWidget(QLabel(f'<html><head/><body><p>P<span style=" vertical-align:sub;">{t-i-1}</span>:</p></body></html>'))
            self.scroll_horizontalLayout.addWidget(delay_element)
            delay_element.setReadOnly(True)
