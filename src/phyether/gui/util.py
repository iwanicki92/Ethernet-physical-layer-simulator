from PyQt5.QtWidgets import QSpinBox, QDoubleSpinBox, QMessageBox

class SpinBoxNoWheel(QSpinBox):
    def wheelEvent(self, event):
        event.ignore()

class DoubleSpinBoxNoWheel(QDoubleSpinBox):
    def wheelEvent(self, event):
        event.ignore()

def create_msg_box(text, title):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setText(text)
        msg_box.setWindowTitle(title)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
