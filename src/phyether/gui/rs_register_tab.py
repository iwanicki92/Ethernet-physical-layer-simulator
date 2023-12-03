from pathlib import Path
from typing import Literal, Optional

from PyQt5.QtWidgets import QWidget, QLineEdit, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSlot

from phyether.gui.ui.rs_register_widget import Ui_rsRegisterForm

from galois import GF, Poly

from phyether.gui.util import create_msg_box

class ReedSolomonRegisterArguments:
    def __init__(self, n: int, k: int, gf: int, primitive_poly: Optional[int] = None,
                 primitive_element: Optional[int] = None,
                 *, repr: Literal['poly', 'int'] = 'poly') -> None:
        self.n = n
        self.k = k
        self.gf = GF(gf,
                     irreducible_poly=primitive_poly,
                     primitive_element=primitive_element,
                     repr=repr)
        self.generating_poly: Optional[Poly] = None

class RSRegisterTab(QWidget, Ui_rsRegisterForm):
    def __init__(self) -> None:
        super().__init__()

        self.rs_param_mapping: dict[str, ReedSolomonRegisterArguments] = {
            "RS(192,186,256) - 25/40GBASE-T": ReedSolomonRegisterArguments(192, 186, 2**8, 0x11D, 2),
            "RS(360,326,1024) - 2.5/5/10GBASE-T1": ReedSolomonRegisterArguments(360, 326, 2**10, 0x409, 2),
            "RS(528,514,1024) - 10/25GBASE-R, 100GBASE-(C/K/S)R4": ReedSolomonRegisterArguments(528, 514, 2**10, 0x409, 2),
            "RS(544,514,1024) - 100GBASE-KP4, 100GBASE-(C/K/S)R2": ReedSolomonRegisterArguments(544, 514, 2**10, 0x409, 2),
        }
        self.current_arguments = self.rs_param_mapping["RS(192,186,256) - 25/40GBASE-T"]

        self.setupUi(self)
        self.delay_elements: list[QLineEdit] = []
        current_dir = Path(__file__).parent
        images = current_dir / "../resources/img"
        self.imageLabel.setPixmap(QPixmap(str(images / "RS_shift_register.png")))
        self.imageLabel.setScaledContents(True)

        self.standardsComboBox.addItems(self.rs_param_mapping.keys())
        self._calculate_gen_poly()


    @pyqtSlot(str)
    def comboBoxChanged(self, new_text: str):
        new_params = self.rs_param_mapping[new_text]
        self.current_arguments = new_params
        self.rs_n_spinBox.setValue(new_params.n)
        self.rs_k_spinBox.setValue(new_params.k)
        self.rs_gf_spinBox.setValue(new_params.gf.degree)
        self.rs_primitive_element_lineEdit.setText(str(new_params.gf.primitive_element))
        self.rs_primitive_poly_lineEdit.setText(str(new_params.gf.irreducible_poly))
        self._calculate_gen_poly()

    @pyqtSlot(bool)
    def poly_repr_checked(self, bool):
        self.current_arguments.gf.repr('int' if bool else 'poly')

    @pyqtSlot()
    def whole_message(self):
        pass

    @pyqtSlot()
    def calculate_generating_poly(self):
        self._calculate_gen_poly()

    @pyqtSlot()
    def next_symbol(self):
        pass

    @pyqtSlot()
    def next_x_symbols(self):
        pass

    @pyqtSlot()
    def calculate_primitives(self):
        try:
            self.current_arguments = ReedSolomonRegisterArguments(
                self.rs_n_spinBox.value(), self.rs_k_spinBox.value(),
                2**self.rs_gf_spinBox.value()
            )
            self._calculate_gen_poly()
        except Exception as ex:
            create_msg_box(f"Error calculating primitives: ", "Error")

    def _calculate_gen_poly(self):
        d = self.current_arguments.n - self.current_arguments.k
        x_poly = Poly.Str('x', self.current_arguments.gf)
        poly = x_poly - self.current_arguments.gf.primitive_element**0
        for i in range(1, d):
            poly *= x_poly - self.current_arguments.gf.primitive_element**i
        self.current_arguments.generating_poly = poly
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
