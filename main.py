from PyQt6.QtCore import Qt, QUrl, QRect, QCoreApplication, QMetaObject, QMimeData, QSize
from qt_templates.ImgGroup.ImgGroup import Ui_Frame as ImgGroup
from qt_templates.MainWindow.MainWindow import Ui_MainWindow as MainWindow
from PyQt6.QtWidgets import QMainWindow, QApplication, QFrame, QFileDialog, QLabel, QPushButton, QSpinBox
from PyQt6.QtGui import QPixmap, QMouseEvent, QDrag, QPainter
from qt_templates.ImgFrame.Img import Ui_Form as Img
import sys
import os
import imghdr
from PyQt6 import QtCore, QtGui, QtWidgets
import PIL
from PIL.ImageQt import ImageQt
import numpy as np
#from PyQt6 import sip

drag_cache = None


def QPixmapToArray(pixmap):
    # Get the size of the current pixmap
    size = pixmap.size()
    h = size.width()
    w = size.height()

    # Get the QImage Item and convert it to a byte string
    qimg = pixmap.toImage()
    byte_str = qimg.bits().tobytes()

    # Using the np.frombuffer function to convert the byte string into an np array
    img = np.frombuffer(byte_str, dtype=np.uint8).reshape((w, h, 4))
    return img


class ImgFrame(QFrame):
    def __init__(self, image, master):
        super().__init__()
        self.ui = Img()
        self.ui.setupUi(self)
        self.master = master
        self.image = image
        self.setImg()
        self.ui.pushButton.setVisible(False)
        self.ui.spinBox.setVisible(False)
        self.ui.pushButton.clicked.connect(self.removeEvent)
        self.ui.pushButton.setText('R')

    def setImg(self):
        self.ui.label.setPixmap(self.image)

    def enterEvent(self, event) -> None:
        self.ui.pushButton.setVisible(True)
        self.ui.spinBox.setVisible(True)

    def leaveEvent(self, a0) -> None:
        self.ui.pushButton.setVisible(False)
        self.ui.spinBox.setVisible(False)

    def removeEvent(self, event) -> None:
        self.master.removeImg(self)

    def mousePressEvent(self, event) -> None:
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.pos()

    def mouseMoveEvent(self, event) -> None:
        # TODO - Make the dragged image really transparent
        if event.buttons() & Qt.MouseButton.LeftButton:
            global drag_cache
            drag_cache = {'master': self.master,
                          'img': self,
                          'index': self.master.images.index(self)}
            drag = QDrag(self)
            mimedata = QMimeData()
            mimedata.setImageData(self.image)
            drag.setMimeData(mimedata)
            pixmap = QPixmap(QSize(150, 150))
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            painter.setOpacity(0.5)
            painter.drawPixmap(QRect(0, 0, 150, 150), self.image)
            painter.drawPixmap(self.rect(), pixmap)
            painter.end()
            drag.setPixmap(pixmap)
            drag.setHotSpot(event.pos())
            # print(self.master.ui.horizontalLayout_2.)
            self.master.removeImg(self)
            self.deleteLater()
            drag.exec()

    # def dragEnterEvent(self, a0) -> None:
    #    print('c')
#
    # def dragMoveEvent(self, a0) -> None:
    #    print('d')
#
    # def dragLeaveEvent(self, a0) -> None:
    #    print('e')


class ImgGroupFrame(QFrame):
    def __init__(self, index: int, master) -> None:
        super().__init__()
        self.ui = ImgGroup()
        self.ui.setupUi(self)
        self.master = master
        self.ui.pushButton.setText("Image")
        self.ui.pushButton_2.setText("Folder")
        self.ui.pushButton_3.setText("Delete")
        self.ui.pushButton_3.clicked.connect(self.delete)
        self.ui.pushButton.clicked.connect(self.add_image)
        self.ui.pushButton_2.clicked.connect(self.add_folder)
        self.images = []

    def delete(self, event) -> None:
        for image in self.images:
            self.ui.horizontalLayout_2.removeWidget(image)
        del self.images
        self.master.verticalLayout.removeWidget(self)
        self.master.groups.remove(self)
        self.deleteLater()

    def add_image(self, event) -> None:
        files = QFileDialog.getOpenFileUrls(
            self, "Open File", QUrl("."),
            "Images (*.png *.jpg *.jpeg *.bmp *.gif, *.rgb, *.pgm, *.ppm, *.tiff, *.rast, *.xbm, *.webp, *.exr)")[0]
        if files:
            images = [QPixmap(file.url().replace('file://', ''))
                      for file in files]
            self.ui.horizontalLayout_2.removeItem(self.ui.spacerItem)
            for image in images:
                widget = ImgFrame(image, self)
                self.ui.horizontalLayout_2.addWidget(widget)
                self.images.append(widget)
            self.ui.horizontalLayout_2.addItem(self.ui.spacerItem)

    def add_folder(self, event) -> None:
        dir = QFileDialog.getExistingDirectory(self, "Open Directory")
        if dir:
            files = []
            for file in [os.path.join(dir, file) for file in os.listdir(dir)]:
                if os.path.isfile(file) and imghdr.what(file):
                    files.append(file)
            images = [QPixmap(file) for file in files]
            self.ui.horizontalLayout_2.removeItem(self.ui.spacerItem)
            for image in images:
                widget = ImgFrame(image, self)
                self.images.append(widget)
                self.ui.horizontalLayout_2.addWidget(widget)
            self.ui.horizontalLayout_2.addItem(self.ui.spacerItem)

    def removeImg(self, img: ImgFrame) -> None:
        # sip.delete(img.ui.label)
        self.ui.horizontalLayout_2.removeWidget(img)
        self.images.remove(img)
        # images = [self.ui.horizontalLayout_2.itemAt(i).widget(
        # ) for i in range(self.ui.horizontalLayout_2.count() - 1)]
        # if len(images) > len(self.images):
        #    for image in images:
        #        if not image in self.images:
        #            self.ui.horizontalLayout_2.removeWidget(image)
        # with open('test.log', 'a') as file:
        #    file.write(
        #        f"self.images: {len(self.images)}, images: {len(images)}\n")


class Stimulus(QMainWindow, MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        super().setupUi(self)
        self.groups = []
        self.pushButton_6.clicked.connect(self.add_imgbox)

    def add_imgbox(self, event):
        self.verticalLayout.removeWidget(self.frame)
        self.verticalLayout.removeItem(self.spacerItem2)
        self.verticalLayout.removeWidget(self.pushButton_6)
        group = ImgGroupFrame(len(self.groups), self)
        self.groups.append(group)
        self.verticalLayout.addWidget(group)
        self.verticalLayout.addWidget(self.frame)
        self.verticalLayout.addItem(self.spacerItem2)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Stimulus()
    window.show()
    app.exec()
