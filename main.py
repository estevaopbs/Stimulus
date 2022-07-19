from __future__ import annotations
from pathlib import Path
from typing import Any, Tuple, Generator
from PyQt6 import QtCore, QtGui, QtWidgets
import numpy as np
from templates.ImgGroup.ImgGroup import Ui_Frame as ImageGroup
from templates.MainWindow.MainWindow import Ui_MainWindow as MainWindow
from templates.Img.Img import Ui_Form as ImageLabel
import sys
import os
from math import floor
import json
from select_images import SelectImages
from itertools import chain
from show import ShowWindow
from PIL.ImageQt import ImageQt
from PIL import Image, UnidentifiedImageError


def is_image(path: Path) -> bool:
    try:
        Image.open(path)
        return True
    except UnidentifiedImageError:
        return False


def get_sys() -> str | None:
    match sys.platform:
        case 'linux':
            return 'linux'
        case 'linux2':
            return 'linux'
        case 'win32':
            return 'windows'
        case _:
            return None


def get_id(n: int = 0) -> Generator[int, None, None]:
    while True:
        yield n
        n += 1


class ImageFrame(QtWidgets.QFrame):
    def __init__(self, file: Path, id: int,
                 master: ImageGroupFrame | None = None,
                 pixmap: QtGui.QPixmap = None,
                 pil_image: ImageQt | None = None, rate: int = 1) -> None:
        super().__init__()
        self.ui = ImageLabel()
        self.ui.setupUi(self)
        self.master = master
        self.pixmap = pixmap
        self.pil_image = pil_image
        self.file = file
        self.id = id
        self.setImg()
        self.ui.pushButton.setVisible(False)
        self.ui.spinBox.setVisible(False)
        self.ui.pushButton.clicked.connect(self.removeEvent)
        self.ui.pushButton.setText('R')
        self.ui.spinBox.setRange(1, 999999)
        self.ui.spinBox.setValue(rate)

    def group_name(self) -> str:
        return self.master.name

    def rate(self) -> int:
        return self.ui.spinBox.value()

    def get_configs(self) -> dict[str, str]:
        return {
            'file': str(self.file),
            'rate': self.rate()
        }

    def setImg(self) -> None:
        if not self.pixmap:
            if self.pil_image is None:
                self.pil_image = ImageQt(self.file)
            self.pixmap = QtGui.QPixmap.fromImage(self.pil_image)
        self.ui.label.setPixmap(self.pixmap)

    def enterEvent(self, event: Any) -> None:
        self.ui.pushButton.setVisible(True)
        self.ui.spinBox.setVisible(True)

    def leaveEvent(self, event: Any) -> None:
        self.ui.pushButton.setVisible(False)
        self.ui.spinBox.setVisible(False)

    def removeEvent(self, event: Any) -> None:
        master_images = self.master.images()
        if self != master_images[-1]:
            master_images[master_images.index(self) + 1].enterEvent(None)
        self.delete()

    def delete(self):
        self.master.removeImg(self)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.buttons() & QtCore.Qt.MouseButton.LeftButton:
            self.master.master.drag_cache = self
            drag = QtGui.QDrag(self)
            mimedata = QtCore.QMimeData()
            mimedata.setImageData(self.pixmap)
            drag.setMimeData(mimedata)
            pixmap = QtGui.QPixmap(QtCore.QSize(150, 150))
            pixmap.fill(QtCore.Qt.GlobalColor.transparent)
            painter = QtGui.QPainter(pixmap)
            painter.setOpacity(0.5)
            painter.drawPixmap(self.rect(), self.pixmap)
            painter.end()
            drag.setPixmap(pixmap)
            drag.setHotSpot(event.pos())
            drag.exec()


class ImageGroupFrame(QtWidgets.QFrame, QtWidgets.QApplication):
    def __init__(self, master: Stimulus, id: int,
                 images: list[ImageFrame] = [], name: str = '') -> None:
        super().__init__()
        self.ui = ImageGroup()
        self.ui.setupUi(self)
        self.master = master
        self.id = id
        self.ui.lineEdit.setText(name)
        self.ui.pushButton.setText("Image")
        self.ui.pushButton_2.setText("Folder")
        self.ui.pushButton_3.setText("Delete")
        self.ui.pushButton_3.clicked.connect(self.delete)
        self.ui.pushButton.clicked.connect(self.addImgEvent)
        self.ui.pushButton_2.clicked.connect(self.addFolderEvent)
        self.setAcceptDrops(True)
        for n, image in enumerate(images):
            self.ui.horizontalLayout_2.insertWidget(n, image)
            image.master = self
        self.ui.spinBox.setRange(1, 999999)
        self.ui.spinBox.setValue(1)

    def rate(self) -> int:
        return self.ui.spinBox.value()

    @property
    def name(self) -> str:
        return self.ui.lineEdit.text()

    def get_configs(self) -> dict[str, str | int | dict[int, dict[str, str]]]:
        return {
            'name': self.name,
            'rate': self.ui.spinBox.value(),
            'images': {image.id: image.get_configs() for image in self.images()}
        }

    def images(self) -> list[ImageFrame]:
        return [self.ui.horizontalLayout_2.itemAt(i).widget() for i in range(self.ui.horizontalLayout_2.count() - 1)]

    def delete(self, event: Any) -> None:
        self.master.removeImgGroupBtn(self)

    def addImg(self, image: ImageFrame) -> None:
        self.ui.horizontalLayout_2.insertWidget(
            self.ui.horizontalLayout_2.count() - 1, image)

    def addImgEvent(self, event: Any) -> None:
        files = QtWidgets.QFileDialog.getOpenFileUrls(
            self, "Open File", QtCore.QUrl("."),
            "Images (*.png *.jpg *.jpeg *.bmp *.gif, *.rgb, *.pgm, *.ppm, *.tiff, *.rast, *.xbm, *.exr, *.webp)")[0]
        for file in files:
            file_ = Path(file.path())
            if is_image(file_):
                self.addImg(ImageFrame(file_, self.master.get_id(), self))

    def addFolderEvent(self, event: Any) -> None:
        dir = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Open Directory")
        if dir:
            for file in [os.path.join(dir, file) for file in os.listdir(dir)]:
                file_ = Path(file)
                if is_image(file_):
                    self.addImg(ImageFrame(file_, self.master.get_id(), self))

    def removeImg(self, img: ImageFrame) -> None:
        img.hide()
        self.ui.horizontalLayout_2.removeWidget(img)

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        if isinstance(self.master.drag_cache, ImageFrame):
            event.accept()
        else:
            event.ignore()

    def dragLeaveEvent(self, event: Any) -> None:
        if isinstance(self.master.drag_cache, ImageFrame):
            image = list(filter(lambda x: x.id ==
                                self.master.drag_cache.id, self.images()))[0]
            self.removeImg(image)

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent) -> None:
        if len(self.images()) == 0:
            self.ui.horizontalLayout_2.insertWidget(
                0, ImageFrame(self.master.drag_cache.file,
                              self.master.drag_cache.id,
                              self,
                              self.master.drag_cache.pixmap,
                              self.master.drag_cache.pil_image,
                              self.master.drag_cache.rate()))
            return
        absolute_pos = event.position().x()
        scroll_relative_pos = absolute_pos + \
            self.ui.scrollArea.horizontalScrollBar().value() - 9
        hovering_index = floor(scroll_relative_pos / 156)
        if hovering_index < 0:
            hovering_index = 0
        if hovering_index >= len(self.images()):
            hovering_index = len(self.images()) - 1
        if (self.ui.horizontalLayout_2.itemAt(hovering_index) is not None and self.ui.horizontalLayout_2.itemAt(hovering_index).widget().id != self.master.drag_cache.id):
            for image in self.images():
                if image.id == self.master.drag_cache.id:
                    self.removeImg(image)
            self.ui.horizontalLayout_2.insertWidget(
                hovering_index, ImageFrame(self.master.drag_cache.file,
                                           self.master.drag_cache.id,
                                           self,
                                           self.master.drag_cache.pixmap,
                                           self.master.drag_cache.pil_image,
                                           self.master.drag_cache.rate()))

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.buttons() & QtCore.Qt.MouseButton.LeftButton:
            self.master.drag_cache = self
            drag = QtGui.QDrag(self)
            mimedata = QtCore.QMimeData()
            drag.setMimeData(mimedata)
            x = self.geometry().x() + self.master.scrollArea_2.geometry().x() + \
                self.master.geometry().x()
            y = self.geometry().y() + self.master.scrollArea_2.geometry().y() + \
                self.master.geometry().y() - self.master.scrollArea_2.verticalScrollBar().value()
            width = self.frameGeometry().width()
            height = self.frameGeometry().height()
            pixmap = QtGui.QPixmap(width, height)
            pixmap.fill(QtCore.Qt.GlobalColor.transparent)
            painter = QtGui.QPainter(pixmap)
            painter.setOpacity(0.5)
            painter.drawPixmap(self.rect(), QtGui.QScreen.grabWindow(
                self.primaryScreen(), x=x, y=y, width=width, height=height))
            painter.end()
            drag.setPixmap(pixmap)
            drag.setHotSpot(event.pos())
            drag.exec()


class Stimulus(QtWidgets.QMainWindow, MainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        super().setupUi(self)
        self.ids_generator = get_id()
        self.get_id = lambda: next(self.ids_generator)
        self.pushButton_6.clicked.connect(self.addImgGroupEvent)
        self.setWindowTitle("Stimulus")
        self.scrollArea_2.setAcceptDrops(True)
        self.scrollArea_2.dragEnterEvent = self.scrollArea2_dragEnterEvent
        self.scrollArea_2.dragMoveEvent = self.scrollArea2_dragMoveEvent
        self.onlyInt = QtGui.QIntValidator()
        self.settinginteractionkey = False
        self.interaction_key_id = None
        self.pushButton.clicked.connect(self.InteractionKeyEvent)
        self.pushButton.wheelEvent = self.wheelEvent
        self.pushButton_5.clicked.connect(self.make_default)
        for lineEdit in self.findChildren(QtWidgets.QLineEdit):
            lineEdit.setValidator(self.onlyInt)
        self.buttonGroup = QtWidgets.QButtonGroup()
        self.buttonGroup_2 = QtWidgets.QButtonGroup()
        self.buttonGroup_3 = QtWidgets.QButtonGroup()
        self.buttonGroup_4 = QtWidgets.QButtonGroup()
        self.buttonGroup.addButton(self.radioButton)
        self.buttonGroup.addButton(self.radioButton_2)
        self.buttonGroup_2.addButton(self.radioButton_3)
        self.buttonGroup_2.addButton(self.radioButton_4)
        self.buttonGroup_3.addButton(self.radioButton_5)
        self.buttonGroup_3.addButton(self.radioButton_6)
        self.buttonGroup_3.addButton(self.radioButton_9)
        self.buttonGroup_4.addButton(self.radioButton_7)
        self.buttonGroup_4.addButton(self.radioButton_8)
        self.buttonGroups = [self.buttonGroup, self.buttonGroup_2,
                             self.buttonGroup_3, self.buttonGroup_4]
        self.pushButton_2.clicked.connect(self.saveSettingsEvent)
        self.pushButton_3.clicked.connect(self.loadSettingsEvent)
        self.pushButton_7.clicked.connect(self.clear)
        for screen in QtWidgets.QApplication.screens():
            self.comboBox.addItem(screen.name())
        self.pushButton_4.clicked.connect(self.startEvent)
        self.drag_cache = None
        self.load_default()

    def clear(self) -> None:
        for group in self.groups():
            self.removeImgGroup(group)
        for buttonGroup in self.buttonGroups:
            buttonGroup.setExclusive(False)
        for radio_button in [self.radioButton, self.radioButton_2,
                             self.radioButton_3, self.radioButton_4,
                             self.radioButton_5, self.radioButton_6,
                             self.radioButton_7, self.radioButton_8,
                             self.radioButton_9]:
            radio_button.setChecked(False)
        for buttonGroup in self.buttonGroups:
            buttonGroup.setExclusive(True)
        for child in self.findChildren(QtWidgets.QCheckBox):
            child.setChecked(False)
        for child in self.findChildren(QtWidgets.QLineEdit):
            child.setText('')
        self.pushButton.setText('Click to set')

    def InteractionKeyEvent(self, event: Any) -> None:
        self.pushButton.setDown(True)
        self.pushButton.setDisabled(True)
        self.pushButton.setStyleSheet("background-color: red;")
        self.settinginteractionkey = True

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        super().keyPressEvent(event)
        if self.settinginteractionkey:
            self.pushButton.setDown(False)
            self.pushButton.setDisabled(False)
            self.pushButton.setStyleSheet("background-color: none;")
            self.settinginteractionkey = False
            key = event.key()
            match key:
                case 16777249:
                    text = "Ctrl"
                case 16777251:
                    text = "Alt"
                case 16777248:
                    text = "Shift"
                case 16781571:
                    text = "AltGr"
                case 16777250:
                    text = "Winkey"
                case _:
                    text = QtGui.QKeySequence(key).toString()
            self.pushButton.setText(text)
            self.interaction_key_id = key

    def groups(self) -> list[ImageGroupFrame]:
        return [self.verticalLayout.itemAt(i).widget() for i in range(self.verticalLayout.count() - 2)]

    def addImgGroupEvent(self, event: Any) -> None:
        self.addImgGroup()

    def addImgGroup(self, images: list[ImageGroupFrame] = [], name: str = '', id: int | None = None, rate: int = 1) -> None:
        if id == None:
            id = self.get_id()
        group = ImageGroupFrame(self, id, images, name)
        self.verticalLayout.insertWidget(
            self.verticalLayout.count() - 2, group)

    def removeImgGroup(self, group: ImageGroupFrame) -> None:
        group.hide()
        for image in group.images():
            group.removeImg(image)
        self.verticalLayout.removeWidget(group)

    def removeImgGroupBtn(self, group: ImageGroupFrame) -> None:
        self.removeImgGroup(group)
        group.deleteLater()

    def scrollArea2_dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        if isinstance(self.drag_cache, ImageGroupFrame):
            event.accept()
        else:
            event.ignore()

    def scrollArea2_dragMoveEvent(self, event: QtGui.QDragMoveEvent) -> None:
        absolute_pos = event.position().y()
        scroll_relative_pos = absolute_pos + \
            self.scrollArea_2.verticalScrollBar().value() - 9
        hovering_index = floor(scroll_relative_pos / 286)
        if hovering_index < 0:
            hovering_index = 0
        if hovering_index >= len(self.groups()):
            hovering_index = len(self.groups()) - 1
        if self.verticalLayout.itemAt(hovering_index) is not None and self.verticalLayout.itemAt(hovering_index).widget().id != self.drag_cache.id:
            group_id = self.drag_cache.id
            name = self.drag_cache.ui.lineEdit.text()
            pixmaps = [image.pixmap for image in self.drag_cache.images()]
            pil_images = [
                image.pil_image for image in self.drag_cache.images()]
            ids = [image.id for image in self.drag_cache.images()]
            files = [image.file for image in self.drag_cache.images()]
            rates = [image.rate() for image in self.drag_cache.images()]
            images = [ImageFrame(file, id, self, pixmap, pil_image, rate)
                      for pixmap, pil_image, id, file, rate in zip(pixmaps, pil_images, ids, files, rates)]
            for group in self.groups():
                if group.id == self.drag_cache.id:
                    self.removeImgGroup(group)
            self.verticalLayout.insertWidget(
                hovering_index, ImageGroupFrame(self, -1, images, name))
            group = list(filter(lambda group: group.id ==
                                -1, self.groups()))[0]
            for image in group.images():
                image.master = group
            group.id = group_id
            self.drag_cache = group

    def intergroup_show_order(self) -> str:
        widgets = list(filter(lambda x: x.isChecked(),
                              self.frame_4.findChildren(QtWidgets.QRadioButton)))
        if widgets:
            return widgets[0].text()

    def intragroup_show_order(self) -> str:
        widgets = list(filter(lambda x: x.isChecked(),
                              self.frame_5.findChildren(QtWidgets.QRadioButton)))
        if widgets:
            return widgets[0].text()

    def intergroup_behaviour(self) -> str:
        widgets = list(filter(lambda x: x.isChecked(),
                              self.frame_6.findChildren(QtWidgets.QRadioButton)))
        if widgets:
            return widgets[0].text()

    def selection_rate_behaviour(self) -> str:
        widgets = list(filter(lambda x: x.isChecked(),
                              self.frame_7.findChildren(QtWidgets.QRadioButton)))
        if widgets:
            return widgets[0].text()

    def allow_image_repeat(self) -> bool:
        return self.checkBox_2.isChecked()

    def amount_of_exhibitions(self) -> int | None:
        text = self.lineEdit.text()
        if self.lineEdit.text():
            return int(text)
        else:
            return None

    def show_time(self) -> int | None:
        text = self.lineEdit_2.text()
        if self.lineEdit_2.text():
            return int(text)
        else:
            return None

    def interval_time(self) -> int | None:
        text = self.lineEdit_3.text()
        if self.lineEdit_3.text():
            return int(text)
        else:
            return None

    def interaction_key(self) -> str:
        return self.pushButton.text()

    def skip_on_click(self) -> bool:
        return self.checkBox_3.isChecked()

    def screen_(self) -> str:
        return self.comboBox.currentText()

    def get_configs(self) -> dict[str, dict[int, dict[str, str | int |
                                                      dict[int, dict[str, str]]]] | str |
                                  int | float | Tuple[int, int] | None]:
        if isinstance(self.interaction_key_id, QtCore.Qt.MouseButton):
            interaction_key_id = self.interaction_key_id.name
        elif isinstance(self.interaction_key_id, int):
            interaction_key_id = self.interaction_key_id
        elif isinstance(self.interaction_key_id, QtCore.QPoint):
            interaction_key_id = (
                self.interaction_key_id.x(), self.interaction_key_id.y())
        else:
            interaction_key_id = None
        if self.groups():
            n = max([group.id for group in self.groups(
            )] + list(chain(*[[image.id for image in group.images()] for group in self.groups()])))
        else:
            n = 0
        configs = {
            'groups': {group.id: group.get_configs() for group in self.groups()},
            'intergroup_show_order': self.intergroup_show_order(),
            'intragroup_show_order': self.intragroup_show_order(),
            'intergroup_behaviour': self.intergroup_behaviour(),
            'selection_rate_behaviour': self.selection_rate_behaviour(),
            'screen': self.screen_(),
            'allow_image_repeat': self.allow_image_repeat(),
            'amount_of_exhibitions': self.amount_of_exhibitions(),
            'show_time': self.show_time(),
            'interval_time': self.interval_time(),
            'interaction_key': interaction_key_id,
            'skip_on_click': self.skip_on_click(),
            'n': n
        }
        return configs

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mousePressEvent(event)
        if self.settinginteractionkey:
            self.pushButton.setDown(False)
            self.pushButton.setDisabled(False)
            self.pushButton.setStyleSheet("background-color: none;")
            self.settinginteractionkey = False
            button = event.button()
            text = button.name
            self.pushButton.setText(text)
            self.interaction_key_id = button

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        super().wheelEvent(event)
        if self.settinginteractionkey:
            self.pushButton.setDown(False)
            self.pushButton.setDisabled(False)
            self.pushButton.setStyleSheet("background-color: none;")
            self.settinginteractionkey = False
            if np.sign(event.angleDelta().y()) == 1:
                self.pushButton.setText('ScrollUp')
            else:
                self.pushButton.setText('ScrollDown')
            self.interaction_key_id = event.angleDelta()

    def make_default(self, event: Any) -> None:
        home_dir = Path.home()
        if not os.path.isdir(home_dir / '.Stimulus'):
            os.mkdir(home_dir / '.Stimulus')
        self.save_settings(home_dir/'.Stimulus/default.json')

    def save_settings(self, path: Path) -> None:
        with open(path, 'w') as file:
            json.dump(self.get_configs(), file, indent=4)

    def load_settings(self, path: Path) -> None:
        with open(path, 'r') as file:
            configs = json.load(file)

            # ids generator
            self.ids_generator = get_id(configs['n'] + 1)

            # intergroup show order
            if configs['intergroup_show_order']:
                next(filter(lambda x: x.text() == configs['intergroup_show_order'],
                            self.frame_4.findChildren(QtWidgets.QRadioButton))).setChecked(True)

            # intragroup show order
            if configs['intragroup_show_order']:
                next(filter(lambda x: x.text() == configs['intragroup_show_order'],
                            self.frame_5.findChildren(QtWidgets.QRadioButton))).setChecked(True)

            # intergroup behaviour
            if configs['intergroup_behaviour']:
                next(filter(lambda x: x.text() == configs['intergroup_behaviour'],
                            self.frame_6.findChildren(QtWidgets.QRadioButton))).setChecked(True)

            # selection rate behaviour
            if configs['selection_rate_behaviour']:
                next(filter(lambda x: x.text() == configs['selection_rate_behaviour'],
                            self.frame_7.findChildren(QtWidgets.QRadioButton))).setChecked(True)

            # screen
            if configs['screen']:
                items = [self.comboBox.itemText(
                    n) for n in range(self.comboBox.count())]
                if configs['screen'] in items:
                    self.comboBox.setCurrentText(configs['screen'])

            # allow image repeat
            if configs['allow_image_repeat']:
                self.checkBox_2.setChecked(True)

            # amount of exhibitions
            if configs['amount_of_exhibitions']:
                self.lineEdit.setText(
                    str(configs['amount_of_exhibitions']))

            # show time
            if configs['show_time']:
                self.lineEdit_2.setText(str(configs['show_time']))

            # interval time
            if configs['interval_time']:
                self.lineEdit_3.setText(str(configs['interval_time']))

            # test key
            if configs['interaction_key']:
                if isinstance(configs['interaction_key'], int):
                    self.interaction_key_id = configs['interaction_key']
                    self.pushButton.setText(QtGui.QKeySequence(
                        configs['interaction_key']).toString())
                elif isinstance(configs['interaction_key'], list):
                    self.interaction_key_id = QtCore.QPoint(
                        0, configs['interaction_key'][1])
                    if np.sign(self.interaction_key_id.y()) == 1:
                        self.pushButton.setText('ScrollUp')
                    else:
                        self.pushButton.setText('ScrollDown')
                else:
                    self.interaction_key_id = QtCore.Qt.MouseButton[configs['interaction_key']]
                    self.pushButton.setText(configs['interaction_key'])

            # skip on click
            if configs['skip_on_click']:
                self.checkBox_3.setChecked(True)

            # images
            if configs['groups']:
                for group in configs['groups']:
                    images = [
                        ImageFrame(Path(configs['groups'][group]['images'][i]['file']), int(i), rate=configs['groups'][group]['images'][i]['rate']) for i in configs['groups'][group]['images']
                    ]
                    self.addImgGroup(
                        images, configs['groups'][group]['name'], int(group), configs['groups'][group]['rate'])

    def load_default(self) -> None:
        home_dir = Path.home()
        if os.path.isdir(home_dir/'.Stimulus'):
            if os.path.isfile(home_dir/'.Stimulus/default.json'):
                self.load_settings(home_dir/'.Stimulus/default.json')

    def saveSettingsEvent(self, event: Any) -> None:
        path = QtWidgets.QFileDialog.getSaveFileName(
            self, 'Save Settings', '', '*.json')
        if len(path) > 0:
            path = path[0]
            if not path.endswith('.json'):
                path += '.json'
            self.save_settings(path)

    def loadSettingsEvent(self, event: Any) -> None:
        path = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Load Settings', '', '*.json')
        if os.path.isfile(path[0]):
            for group in self.groups():
                self.removeImgGroup(group)
            self.load_settings(path[0])

    def isDeterministicValid(self) -> bool:
        if str(self.amount_of_exhibitions()).isnumeric():
            if self.amount_of_exhibitions() % sum([group.rate() for group in self.groups()]) != 0:
                return False
        groups_load_unity = self.amount_of_exhibitions() / \
            sum([group.rate() for group in self.groups()])
        for group in self.groups():
            if (group.rate() * groups_load_unity) % sum([img.rate() for img in group.images()]) != 0:
                return False
        return True

    def validate_settings(self) -> bool:
        text = ''
        if not self.intergroup_show_order():
            text += 'Please select intergroup show order.\n'
        if not self.intragroup_show_order():
            text += 'Please select intragroup show order.\n'
        if not self.intergroup_behaviour():
            text += 'Please select intergroup behaviour.\n'
        if not self.selection_rate_behaviour():
            text += 'Please select selection rate behaviour.\n'
        if not self.amount_of_exhibitions():
            text += 'Please enter amount of exhibitions.\n'
        elif not self.allow_image_repeat() and sum([len(group.images()) for group in self.groups()]) < self.amount_of_exhibitions():
            text += "Amount of exhibitions can't be greater than the total amount of images if images aren't allowed to repeat.\n"
        if not self.show_time():
            text += 'Please enter show time.\n'
        if self.interval_time() is None:
            text += 'Please enter interval time.\n'
        if self.interaction_key() == 'Click to set':
            text += 'Please set interaction key.\n'
        if not self.groups():
            text += 'Please add at least one group.\n'
        for group in self.groups():
            if not group.images():
                text += 'All groups must have at least one image.\n'
                break
        for group in self.groups():
            if not group.name:
                text += 'All groups must have a name.\n'
                break
        if self.intergroup_show_order() == 'Sequential' \
           and self.intragroup_show_order() == 'Sequential' \
           and self.selection_rate_behaviour() == 'Probabilistic':
            text += "When intergroup and intragroup show order are both sequential selection rate behaviour can't be probabilistic.\n"
        if self.selection_rate_behaviour() == 'Deterministic' and not self.isDeterministicValid():
            text += "Amount of exhibitions must be divisible by the sum of all group rates and the amount of exhibitions for each group must be divisible by the sum of all group's images rates.\n"
        if self.selection_rate_behaviour() == 'Probabilistic' and self.intergroup_behaviour() == 'Select a new group on depletion\nof the current':
            text += "When intergroup behaviour is set to select a new group on depletion of the current, selection rate behaviour can't be probabilistic.\n"
        text = text.strip('\n')
        if text:
            QtWidgets.QMessageBox.warning(self, 'Error', text)
            return False
        return True

    def startEvent(self, event: Any) -> None:
        if self.validate_settings():
            all_images = list(chain(*[group.images()
                              for group in self.groups()]))
            images = []
            for image in SelectImages(**self.get_configs()).run():
                images.append(
                    next(filter(lambda img: img.id == image.id, all_images)))
            args = {
                'master': self,
                'images': [{
                    'file': str(image.file),
                    'group_name': image.group_name(),
                    'pixmap': image.pixmap
                } for image in images],
                'show_time': self.show_time(),
                'interval_time': self.interval_time(),
                'interaction_key': self.interaction_key_id,
                'skip_on_click': self.skip_on_click(),
                'screen': self.screen_()
            }
            ShowWindow(**args)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Stimulus()
    window.show()
    app.exec()

# TODO: CONSERTAR TAB
# TODO: ESTILIZAÇÂO COM CSS
# TODO: ADICIONAR SUPORTE AS TECLAS DIRECIONAIS
# TODO: AUMENTAR O TAMANHO DO FRAME ESQUERDO QUANDO APARECER A SCROLLBAR
# TODO: PERMITIR RATE = 0
# TODO: JANELA DE MONITORAMENTO
# TODO: DRAG SCROLL
# TODO: FIX GUI FREEZING
