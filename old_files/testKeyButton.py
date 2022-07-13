from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QMouseEvent


class testKeyButton(QPushButton):
    def __init__(self, parent, master=None):
        super().__init__(parent)
        self.master = master

    def mousePressEvent(self, event: QMouseEvent) -> None:
        super().mousePressEvent(event)
        if self.master.settingtestkey:
            # self.setFocus()
            self.setDown(False)
            self.setDisabled(False)
            self.setStyleSheet("background-color: none;")
            self.master.settingtestkey = False
            button = event.button()
            text = button.name
            self.setText(text)
            self.master.test_key_id = button
