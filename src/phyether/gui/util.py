from PyQt5.QtWidgets import QSpinBox, QDoubleSpinBox

class SpinBoxNoWheel(QSpinBox):
    def wheelEvent(self, event):
        event.ignore()

class DoubleSpinBoxNoWheel(QDoubleSpinBox):
    def wheelEvent(self, event):
        event.ignore()
