from abc import abstractmethod
from typing import Tuple
from PyQt5.QtGui import QValidator

class ListValidator(QValidator):
    def __init__(self, max_items) -> None:
        super().__init__()
        self.max_items = max_items

    @abstractmethod
    def validate_item(self, item: str) -> QValidator.State:
        ...

    def validate(self, a0: str, a1: int) -> Tuple[QValidator.State, str, int]:
        valid = QValidator.State.Acceptable
        items = a0.split()
        if len(items) > self.max_items:
            return QValidator.State.Invalid, a0, a1
        for num in items:
            new_valid = self.validate_item(num)
            if new_valid == QValidator.State.Intermediate:
                valid = new_valid
            elif new_valid == QValidator.State.Invalid:
                valid = new_valid
                break

        return valid, a0, a1


class IntListValidator(ListValidator):
    def __init__(self, max, *args) -> None:
        super().__init__(*args)
        self.max = max

    def validate_item(self, item: str) -> QValidator.State:
        try:
            val = int(item)
            if 0 <= val <= self.max:
                return QValidator.State.Acceptable
            else:
                return QValidator.State.Invalid
        except Exception as ex:
            return QValidator.State.Invalid


class HexListValidator(ListValidator):
    def __init__(self, max, *args) -> None:
        super().__init__(*args)
        self.max = max

    def validate_item(self, item: str) -> QValidator.State:
        try:
            val = int(item, 16)
            if 0 <= val <= self.max:
                return QValidator.State.Acceptable
            else:
                return QValidator.State.Invalid
        except Exception as ex:
            return QValidator.State.Invalid


class BinListValidator(ListValidator):
    def __init__(self, max_bits, *args) -> None:
        super().__init__(*args)
        self.max = max_bits

    def fixup(self, a0: str) -> str:
        return ' '.join([num.rjust(self.max, '0') for num in a0.split()])

    def validate_item(self, item: str) -> QValidator.State:
        try:
            int(item, 2)
            if len(item) < self.max:
                return QValidator.State.Intermediate
            elif len(item) > self.max:
                return QValidator.State.Invalid
            else:
                return QValidator.State.Acceptable
        except Exception as ex:
            return QValidator.State.Invalid
