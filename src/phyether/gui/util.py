import sys
from traceback import print_exc
from typing import Union

from PyQt5.QtWidgets import QSpinBox, QDoubleSpinBox, QMessageBox, QDesktopWidget, QStyle
from PyQt5 import QtCore

class SpinBoxNoWheel(QSpinBox):
    def wheelEvent(self, event):
        event.ignore()

class DoubleSpinBoxNoWheel(QDoubleSpinBox):
    def wheelEvent(self, event):
        event.ignore()

def create_msg_box(text: str, title: str, *,
                   icon: QMessageBox.Icon = QMessageBox.Icon.Critical,
                   buttons: Union[QMessageBox.StandardButtons, QMessageBox.StandardButton] = QMessageBox.StandardButton.Ok
                   ) -> QMessageBox.StandardButton:
        if any("debug" in arg.lower() for arg in sys.argv):
             print_exc()
             print(f"create_msg_box: {text=}, {title=}")
        desktop = QDesktopWidget()
        msg_box = QMessageBox()
        msg_box.setIcon(icon)
        msg_box.setText(text)
        msg_box.setWindowTitle(title)
        msg_box.setStandardButtons(buttons)
        msg_box.move(int((desktop.width() - msg_box.width()) / 2),
                     int((desktop.height() - msg_box.height()) / 2))
        return QMessageBox.StandardButton(msg_box.exec())
