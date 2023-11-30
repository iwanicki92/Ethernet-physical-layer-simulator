from pathlib import Path

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSlot
from attr import define

from phyether.gui.ui.rs_register_widget import Ui_rsRegisterForm
from phyether.util import DictMapping

@define(slots=False)
class ReedSolomonRegisterArguments(DictMapping):
    n: int
    k: int
    gf_power: int
    primitive_poly: int
    primitive_element: int

class RSRegisterTab(QWidget, Ui_rsRegisterForm):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        current_dir = Path(__file__).parent
        images = current_dir / "../resources/img"
        self.imageLabel.setPixmap(QPixmap(str(images / "RS_shift_register.png")))
        self.imageLabel.setScaledContents(True)

        self.rs_param_mapping: dict[str, ReedSolomonRegisterArguments] = {
            "RS(192,186,256) - 25/40GBASE-T": ReedSolomonRegisterArguments(192, 186, 8, 0x11D, 2),
            "RS(360,326,1024) - 2.5/5/10GBASE-T1": ReedSolomonRegisterArguments(360, 326, 10, 0x409, 2),
            "RS(528,514,1024) - 10/25GBASE-R, 100GBASE-(C/K/S)R4": ReedSolomonRegisterArguments(528, 514, 1024, 0x409, 2),
            "RS(544,514,1024) - 100GBASE-KP4, 100GBASE-(C/K/S)R2": ReedSolomonRegisterArguments(544, 514, 1024, 0x409, 2),
        }

        self.standardsComboBox.addItems(self.rs_param_mapping.keys())

    @pyqtSlot(str)
    def comboBoxChanged(self, new_text: str):
        new_params = self.rs_param_mapping[new_text]
        self.rs_n_spinBox.setValue(new_params.n)
        self.rs_k_spinBox.setValue(new_params.k)
        self.rs_gf_spinBox.setValue(new_params.gf_power)
        self.rs_primitive_element_lineEdit.setText(f"{new_params.primitive_element:X}")
        self.rs_primitive_poly_lineEdit.setText(f"{new_params.primitive_poly:X}")
