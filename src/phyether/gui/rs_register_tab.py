import sys
from pathlib import Path
from typing import Literal, Optional

from PyQt5.QtWidgets import QWidget, QLineEdit, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSlot

from phyether.gui.ui.rs_register_widget import Ui_rsRegisterForm

from galois import GF, Poly

from phyether.gui.util import create_msg_box
from phyether.reed_solomon_bch import BCH_RS

class ReedSolomonRegisterArguments:
    def __init__(self, n: int, k: int, gf: int, primitive_poly: Optional[int] = None,
                 primitive_element: Optional[int] = None,
                 *, repr: Literal['poly', 'int', 'power'] = 'poly') -> None:
        self.n = n
        self.k = k
        self._primitive_poly = primitive_poly
        self._primitive_element = primitive_element
        self.gf = GF(gf,
                     irreducible_poly=primitive_poly,
                     primitive_element=primitive_element,
                     repr=repr)
        self.generating_poly: Optional[Poly] = None

    def copy(self):
        return ReedSolomonRegisterArguments(self.n, self.k, self.gf.order,
                                            self._primitive_poly, self._primitive_element,
                                            repr=self.gf.element_repr)

class RSRegisterTab(QWidget, Ui_rsRegisterForm):
    def __init__(self) -> None:
        super().__init__()

        self.rs_param_mapping: dict[str, ReedSolomonRegisterArguments] = {
            "RS(192,186,256) - 25/40GBASE-T": ReedSolomonRegisterArguments(192, 186, 2**8, 0x11D, 2),
            "RS(360,326,1024) - 2.5/5/10GBASE-T1": ReedSolomonRegisterArguments(360, 326, 2**10, 0x409, 2),
            "RS(528,514,1024) - 10/25GBASE-R, 100GBASE-(C/K/S)R4": ReedSolomonRegisterArguments(528, 514, 2**10, 0x409, 2),
            "RS(544,514,1024) - 100GBASE-KP4, 100GBASE-(C/K/S)R2": ReedSolomonRegisterArguments(544, 514, 2**10, 0x409, 2),
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
                create_msg_box("Error", f"Couldn't parse arguments: {ex}")
        self.standardsComboBox.addItems(self.rs_param_mapping.keys())
        self._calculate_gen_poly()
        self.bch = BCH_RS(self.current_arguments.n, self.current_arguments.k, self.current_arguments.gf, self.current_arguments.generating_poly)


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

    @pyqtSlot(bool)
    def poly_repr_checked(self, bool):
        poly_or_int = 'int' if bool else 'poly'
        for params in self.rs_param_mapping.values():
            params.gf.repr(poly_or_int)
        self.current_arguments.gf.repr(poly_or_int)
        self.rs_primitive_element_lineEdit.setText(str(self.current_arguments.gf.primitive_element))
        self.rs_primitive_poly_lineEdit.setText(str(self.current_arguments.gf.irreducible_poly))
        poly = str(self.current_arguments.generating_poly) if self.current_arguments.generating_poly is not None else ""
        self.gen_poly_lineEdit.setText(poly)

    @pyqtSlot(int)
    def gf_changed(self, value):
        self.fillSpinBox.setMaximum(2**value - 1)

    @pyqtSlot()
    def whole_message(self):
        pass

    @pyqtSlot()
    def calculate_generating_poly(self):
        self._calculate_gen_poly()
        self._clear()

    @pyqtSlot()
    def next_symbol(self):
        symbols = self.input_lineEdit.text().split()
        self.input_lineEdit.setText(' '.join(symbols[1:]))
        output = self.output_lineEdit.text()
        if self.bch.i >= self.current_arguments.k:
            symbol = None
        elif symbols:
            symbol = symbols[0]
        else:
            symbol = self.fillSpinBox.value()
        encoded = self.bch.encode_next_symbol(symbol)
        self.output_lineEdit.setText(output + " " + str(encoded))
        self.update_parity()

    @pyqtSlot()
    def next_x_symbols(self):
        pass

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
                2**self.rs_gf_spinBox.value()
            )
            self._calculate_gen_poly()
            self.output_lineEdit.setText("")
        except Exception as ex:
            create_msg_box(f"Error calculating primitives: ", "Error")

    def _calculate_gen_poly(self):
        d = self.current_arguments.n - self.current_arguments.k
        x_poly = Poly.Str('x', self.current_arguments.gf)
        poly = x_poly - self.current_arguments.gf.primitive_element**0
        for i in range(1, d):
            poly *= x_poly - self.current_arguments.gf.primitive_element**i
        self.current_arguments.generating_poly = poly
        self.output_lineEdit.setText("")
        self.bch = BCH_RS(self.current_arguments.n, self.current_arguments.k, self.current_arguments.gf, self.current_arguments.generating_poly)
        self.gen_poly_lineEdit.setText(str(poly))
        self.delay_elements = [QLineEdit() for _ in range(d)]

        from PyQt5.QtWidgets import QAbstractScrollArea, QHBoxLayout
        self.scrollArea: QAbstractScrollArea
        self.scrollAreaWidgetContents: QWidget
        self.scroll_horizontalLayout: QHBoxLayout

        for i in reversed(range(self.scroll_horizontalLayout.count())):
            widget = self.scroll_horizontalLayout.itemAt(i).widget()
            self.scroll_horizontalLayout.removeWidget(widget)

        for i, delay_element in enumerate(self.delay_elements):
            self.scroll_horizontalLayout.addWidget(QLabel(f'<html><head/><body><p>P<span style=" vertical-align:sub;">{d-i-1}</span>:</p></body></html>'))
            self.scroll_horizontalLayout.addWidget(delay_element)
