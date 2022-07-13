from PyQt6 import QtGui, QtCore, QtWidgets
from PyQt6.QtCore import Qt
from pathlib import Path
import random
from qt_templates.Show.Show import Ui_MainWindow as Show
import sys


class ShowWindow(QtWidgets.QMainWindow, Show):
    def __init__(self, parent=None):
        super(ShowWindow, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Show")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint |
                            Qt.WindowType.WindowDoesNotAcceptFocus |
                            Qt.WindowType.WindowStaysOnTopHint)

        self.showFullScreen()


if __name__ == '__main__':
    test = QtWidgets.QApplication(sys.argv)
    test_window = ShowWindow()
    test_window.show()
    test.exec()
