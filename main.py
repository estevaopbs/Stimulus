from PyQt6.QtCore import Qt, QUrl, QMimeData, QSize
from qt_templates.ImgGroup.ImgGroup import Ui_Frame as ImgGroup
from qt_templates.MainWindow.MainWindow import Ui_MainWindow as MainWindow
from PyQt6.QtWidgets import QMainWindow, QApplication, QFrame, QFileDialog
from PyQt6.QtGui import QPixmap, QDrag, QPainter, QScreen
from qt_templates.Img.Img import Ui_Form as Img
import sys
import os
import imghdr
from PyQt6 import sip
from math import floor

drag_cache = None
drop_cache = None


def get_id():
    n = -1
    while True:
        n += 1
        yield n


class ImgFrame(QFrame):
    def __init__(self, image, master, id, adress):
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
        self.id = id
        self.adress = adress

    def setImg(self):
        self.ui.label.setPixmap(self.image)

    def enterEvent(self, event) -> None:
        self.ui.pushButton.setVisible(True)
        self.ui.spinBox.setVisible(True)

    def leaveEvent(self, a0) -> None:
        self.ui.pushButton.setVisible(False)
        self.ui.spinBox.setVisible(False)

    def removeEvent(self, event) -> None:
        self.delete()

    def delete(self):
        self.master.removeImg(self)

    def mouseMoveEvent(self, event) -> None:
        # TODO - Make the dragged image really transparent
        if event.buttons() & Qt.MouseButton.LeftButton:
            global drag_cache
            drag_cache = {
                'img': self
            }
            drag = QDrag(self)
            mimedata = QMimeData()
            mimedata.setImageData(self.image)
            drag.setMimeData(mimedata)
            pixmap = QPixmap(QSize(150, 150))
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            painter.setOpacity(0.5)
            painter.drawPixmap(self.rect(), self.image)
            painter.end()
            drag.setPixmap(pixmap)
            drag.setHotSpot(event.pos())
            drag.exec()


class ImgGroupFrame(QFrame, QApplication):
    def __init__(self, master, id, images=[], name='') -> None:
        super().__init__()
        self.ui = ImgGroup()
        self.ui.setupUi(self)
        self.master = master
        self.id = id
        if len(images) > 0:
            self.pixmaps = [image.image for image in images]
        self.ui.lineEdit.setText(name)
        self.ui.pushButton.setText("Image")
        self.ui.pushButton_2.setText("Folder")
        self.ui.pushButton_3.setText("Delete")
        self.ui.pushButton_3.clicked.connect(self.delete)
        self.ui.pushButton.clicked.connect(self.addImg)
        self.ui.pushButton_2.clicked.connect(self.addFolder)
        self.setAcceptDrops(True)
        for n, image in enumerate(images):
            self.ui.horizontalLayout_2.insertWidget(n, image)

    def update_images(self):
        self.pixmaps = [image.image for image in self.images()]

    def images(self):
        return [self.ui.horizontalLayout_2.itemAt(i).widget() for i in range(self.ui.horizontalLayout_2.count() - 1)]

    def delete(self, event) -> None:
        self.master.removeImgGroupBtn(self)
        self.update_images()

    def addImg(self, event) -> None:
        files = QFileDialog.getOpenFileUrls(
            self, "Open File", QUrl("."),
            "Images (*.png *.jpg *.jpeg *.bmp *.gif, *.rgb, *.pgm, *.ppm, *.tiff, *.rast, *.xbm, *.webp, *.exr)")[0]
        if files:
            images = [QPixmap(file.url().replace('file://', ''))
                      for file in files]
            self.ui.horizontalLayout_2.removeItem(self.ui.spacerItem)
            for file, image in zip(files, images):
                widget = ImgFrame(image, self, self.master.get_id(), file)
                self.ui.horizontalLayout_2.addWidget(widget)
            self.ui.horizontalLayout_2.addItem(self.ui.spacerItem)
        self.update_images()

    def addFolder(self, event) -> None:
        dir = QFileDialog.getExistingDirectory(self, "Open Directory")
        if dir:
            files = []
            for file in [os.path.join(dir, file) for file in os.listdir(dir)]:
                if os.path.isfile(file) and imghdr.what(file):
                    files.append(file)
            images = [QPixmap(file) for file in files]
            self.ui.horizontalLayout_2.removeItem(self.ui.spacerItem)
            for file, image in zip(files, images):
                widget = ImgFrame(image, self, self.master.get_id(), file)
                self.ui.horizontalLayout_2.addWidget(widget)
            self.ui.horizontalLayout_2.addItem(self.ui.spacerItem)
        self.update_images()

    def removeImg(self, img: ImgFrame) -> None:
        sip.delete(img.ui.label)
        self.ui.horizontalLayout_2.removeWidget(img)
        self.update_images()

    def dragEnterEvent(self, event) -> None:
        global drag_cache
        if 'img' in drag_cache:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event) -> None:
        global drag_cache
        absolute_pos = event.position().x()
        scroll_relative_pos = absolute_pos + \
            self.ui.scrollArea.horizontalScrollBar().value() - 9
        hovering_index = floor(scroll_relative_pos / 156)
        if hovering_index < 0:
            hovering_index = 0
        if hovering_index >= len(self.images()):
            hovering_index = len(self.images()) - 1
        if self.ui.horizontalLayout_2.itemAt(hovering_index) is not None and self.ui.horizontalLayout_2.itemAt(hovering_index).widget().id != drag_cache['img'].id:
            for image in self.images():
                if image.id == drag_cache['img'].id:
                    self.removeImg(image)
            self.ui.horizontalLayout_2.insertWidget(
                hovering_index, ImgFrame(drag_cache['img'].image, self, drag_cache['img'].id, drag_cache['img'].adress))
        self.update_images()

    def mouseMoveEvent(self, event) -> None:
        # TODO - Make the dragged image really transparent
        if event.buttons() & Qt.MouseButton.LeftButton:
            global drag_cache
            drag_cache = {
                'group': self
            }
            drag = QDrag(self)
            mimedata = QMimeData()
            drag.setMimeData(mimedata)
            x = self.geometry().x() + self.master.scrollArea_2.geometry().x() + \
                self.master.geometry().x()
            y = self.geometry().y() + self.master.scrollArea_2.geometry().y() + \
                self.master.geometry().y() - self.master.scrollArea_2.verticalScrollBar().value()
            width = self.frameGeometry().width()
            height = self.frameGeometry().height()
            pixmap = QPixmap(width, height)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            painter.setOpacity(0.5)
            painter.drawPixmap(self.rect(), QScreen.grabWindow(
                self.primaryScreen(), x=x, y=y, width=width, height=height))
            painter.end()
            drag.setPixmap(pixmap)
            drag.setHotSpot(event.pos())
            drag.exec()


class Stimulus(QMainWindow, MainWindow, QApplication):
    def __init__(self, parent=None):
        super().__init__(parent)
        super().setupUi(self)
        self.ids_generator = get_id()
        self.get_id = lambda: next(self.ids_generator)
        self.pushButton_6.clicked.connect(self.addImgGroup)
        self.setWindowTitle("Stimulus")
        self.scrollArea_2.setAcceptDrops(True)
        self.scrollArea_2.dragEnterEvent = self.scrollArea2_dragEnterEvent
        self.scrollArea_2.dragMoveEvent = self.scrollArea2_dragMoveEvent
        self.delete_on_drag = []

    def groups(self):
        return [self.verticalLayout.itemAt(i).widget() for i in range(self.verticalLayout.count() - 2)]

    def addImgGroup(self, event):
        self.verticalLayout.removeWidget(self.frame)
        self.verticalLayout.removeItem(self.spacerItem2)
        self.verticalLayout.removeWidget(self.pushButton_6)
        group = ImgGroupFrame(self, self.get_id())
        self.verticalLayout.addWidget(group)
        self.verticalLayout.addWidget(self.frame)
        self.verticalLayout.addItem(self.spacerItem2)

    def removeImgGroup(self, group: ImgGroupFrame) -> None:
        for image in group.images():
            group.removeImg(image)
        self.verticalLayout.removeWidget(group)

    def removeImgGroupBtn(self, group: ImgGroupFrame) -> None:
        self.removeImgGroup(group)
        group.deleteLater()

    def scrollArea2_dragEnterEvent(self, event):
        global drag_cache
        if 'group' in drag_cache:
            event.accept()
        else:
            event.ignore()

    def scrollArea2_dragMoveEvent(self, event) -> None:
        global drag_cache
        absolute_pos = event.position().y()
        scroll_relative_pos = absolute_pos + \
            self.scrollArea_2.verticalScrollBar().value() - 9
        hovering_index = floor(scroll_relative_pos / 286)
        if hovering_index < 0:
            hovering_index = 0
        if hovering_index >= len(self.groups()):
            hovering_index = len(self.groups()) - 1
        self.setWindowTitle(str(self.groups()))
        if self.verticalLayout.itemAt(hovering_index) is not None and self.verticalLayout.itemAt(hovering_index).widget().id != drag_cache['group'].id:
            group_id = drag_cache['group'].id
            name = drag_cache['group'].ui.lineEdit.text()
            pixmaps = [image.image for image in drag_cache['group'].images()]
            ids = [image.id for image in drag_cache['group'].images()]
            files = [image.adress for image in drag_cache['group'].images()]
            images = [ImgFrame(pixmap, self, id, file)
                      for pixmap, id, file in zip(pixmaps, ids, files)]
            for group in self.groups():
                if group.id == drag_cache['group'].id:
                    self.removeImgGroup(group)
            self.verticalLayout.insertWidget(
                hovering_index, ImgGroupFrame(self, -1, images, name))
            group = list(filter(lambda group: group.id ==
                                -1, self.groups()))[0]
            for image in group.images():
                image.master = group
            group.id = group_id
            drag_cache['group'] = group


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Stimulus()
    window.show()
    app.exec()

# TODO: TIRAR VARIAVEIS GLOBAIS
# TODO: TIRAR VALORES HARD-CODED
# TODO: DEIXAR DICIONARIO COMO VARIAVEL NORMAL, DESFAZER DICIONARIO
