from pathlib import Path
from PyQt6.QtCore import Qt, QUrl, QMimeData, QSize, QPoint
from numpy import sign
from qt_templates.ImgGroup.ImgGroup import Ui_Frame as ImgGroup
from qt_templates.MainWindow.MainWindow import Ui_MainWindow as MainWindow
from PyQt6.QtWidgets import QMainWindow, QApplication, QFrame, QFileDialog, QRadioButton, QLineEdit, QCheckBox, QButtonGroup
from PyQt6.QtGui import QPixmap, QDrag, QPainter, QScreen, QIntValidator, QKeyEvent, QKeySequence, QMouseEvent, QWheelEvent
from qt_templates.Img.Img import Ui_Form as Img
import sys
import os
import imghdr
from math import floor
import json
from pprint import pprint

drag_cache = None
drop_cache = None


def get_sys():
    match sys.platform:
        case 'linux':
            return 'linux'
        case 'linux2':
            return 'linux'
        case 'win32':
            return 'windows'


def get_id():
    n = 0
    while True:
        yield n
        n += 1


class ImgFrame(QFrame):
    def __init__(self, file, id, master=None, pixmap=None, rate=1):
        super().__init__()
        self.ui = Img()
        self.ui.setupUi(self)
        self.master = master
        self.pixmap = pixmap
        self.file = file
        self.id = id
        self.setImg()
        self.ui.pushButton.setVisible(False)
        self.ui.spinBox.setVisible(False)
        self.ui.pushButton.clicked.connect(self.removeEvent)
        self.ui.pushButton.setText('R')
        self.ui.spinBox.setRange(0, 999999)
        self.ui.spinBox.setValue(rate)

    @property
    def rate(self):
        return self.ui.spinBox.value()

    def get_configs(self):
        return {
            'file': self.file,
            'rate': self.ui.spinBox.value()
        }

    def setImg(self):
        if not self.pixmap:
            self.pixmap = QPixmap(self.file)
        self.ui.label.setPixmap(self.pixmap)

    def enterEvent(self, event) -> None:
        self.ui.pushButton.setVisible(True)
        self.ui.spinBox.setVisible(True)

    def leaveEvent(self, a0) -> None:
        self.ui.pushButton.setVisible(False)
        self.ui.spinBox.setVisible(False)

    def removeEvent(self, event) -> None:
        master_images = self.master.images()
        if len(master_images) > 1:
            master_images[master_images.index(self) + 1].enterEvent(None)
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
            mimedata.setImageData(self.pixmap)
            drag.setMimeData(mimedata)
            pixmap = QPixmap(QSize(150, 150))
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            painter.setOpacity(0.5)
            painter.drawPixmap(self.rect(), self.pixmap)
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
        self.ui.spinBox.setRange(0, 999999)
        self.ui.spinBox.setValue(1)

    @property
    def name(self):
        return self.ui.lineEdit.text()

    def get_configs(self):
        return {
            'name': self.name,
            'rate': self.ui.spinBox.value(),
            'images': {image.id: image.get_configs() for image in self.images()}
        }

    def images(self):
        return [self.ui.horizontalLayout_2.itemAt(i).widget() for i in range(self.ui.horizontalLayout_2.count() - 1)]

    def delete(self, event) -> None:
        self.master.removeImgGroupBtn(self)

    def addImg(self, image: ImgFrame) -> None:
        self.ui.horizontalLayout_2.insertWidget(
            self.ui.horizontalLayout_2.count() - 1, image)

    def addImgEvent(self, event) -> None:
        files = QFileDialog.getOpenFileUrls(
            self, "Open File", QUrl("."),
            "Images (*.png *.jpg *.jpeg *.bmp *.gif, *.rgb, *.pgm, *.ppm, *.tiff, *.rast, *.xbm, *.webp, *.exr)")[0]
        for file in files:
            self.addImg(ImgFrame(file, self.master.get_id(), self))

    def addFolderEvent(self, event) -> None:
        dir = QFileDialog.getExistingDirectory(self, "Open Directory")
        if dir:
            files = []
            for file in [os.path.join(dir, file) for file in os.listdir(dir)]:
                if os.path.isfile(file) and imghdr.what(file):
                    files.append(file)
            for file in files:
                self.addImg(ImgFrame(file, self.master.get_id(), self))

    def removeImg(self, img: ImgFrame) -> None:
        img.hide()
        self.ui.horizontalLayout_2.removeWidget(img)

    def dragEnterEvent(self, event) -> None:
        global drag_cache
        if 'img' in drag_cache:
            event.accept()
        else:
            event.ignore()

    def dragLeaveEvent(self, event) -> None:
        global drag_cache
        if 'img' in drag_cache:
            image = list(filter(lambda x: x.id ==
                                drag_cache['img'].id, self.images()))[0]
            self.removeImg(image)

    def dragMoveEvent(self, event) -> None:
        global drag_cache
        if len(self.images()) == 0:
            self.ui.horizontalLayout_2.insertWidget(
                0, ImgFrame(drag_cache['img'].file, drag_cache['img'].id, self, drag_cache['img'].pixmap, drag_cache['img'].rate))
            return
        absolute_pos = event.position().x()
        scroll_relative_pos = absolute_pos + \
            self.ui.scrollArea.horizontalScrollBar().value() - 9
        hovering_index = floor(scroll_relative_pos / 156)
        if hovering_index < 0:
            hovering_index = 0
        if hovering_index >= len(self.images()):
            hovering_index = len(self.images()) - 1
        if (self.ui.horizontalLayout_2.itemAt(hovering_index) is not None and self.ui.horizontalLayout_2.itemAt(hovering_index).widget().id != drag_cache['img'].id):
            for image in self.images():
                if image.id == drag_cache['img'].id:
                    self.removeImg(image)
            self.ui.horizontalLayout_2.insertWidget(
                hovering_index, ImgFrame(drag_cache['img'].file, drag_cache['img'].id, self, drag_cache['img'].pixmap, drag_cache['img'].rate))

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
        self.pushButton_6.clicked.connect(self.addImgGroupEvent)
        self.setWindowTitle("Stimulus")
        self.scrollArea_2.setAcceptDrops(True)
        self.scrollArea_2.dragEnterEvent = self.scrollArea2_dragEnterEvent
        self.scrollArea_2.dragMoveEvent = self.scrollArea2_dragMoveEvent
        self.onlyInt = QIntValidator()
        self.settingtestkey = False
        self.test_key_id = None
        self.pushButton.clicked.connect(self.TestKeyEvent)
        self.pushButton.wheelEvent = self.wheelEvent
        self.pushButton_5.clicked.connect(self.make_default)
        for lineEdit in self.findChildren(QLineEdit):
            lineEdit.setValidator(self.onlyInt)
        self.load_default()
        self.buttonGroup = QButtonGroup()
        self.buttonGroup_2 = QButtonGroup()
        self.buttonGroup_3 = QButtonGroup()
        self.buttonGroup_4 = QButtonGroup()
        self.buttonGroup.addButton(self.radioButton)
        self.buttonGroup.addButton(self.radioButton_2)
        self.buttonGroup_2.addButton(self.radioButton_3)
        self.buttonGroup_2.addButton(self.radioButton_4)
        self.buttonGroup_3.addButton(self.radioButton_5)
        self.buttonGroup_3.addButton(self.radioButton_6)
        self.buttonGroup_4.addButton(self.radioButton_7)
        self.buttonGroup_4.addButton(self.radioButton_8)
        self.buttonGroups = [self.buttonGroup, self.buttonGroup_2,
                             self.buttonGroup_3, self.buttonGroup_4]
        self.pushButton_2.clicked.connect(self.saveSettingsEvent)
        self.pushButton_3.clicked.connect(self.loadSettingsEvent)
        self.pushButton_7.clicked.connect(self.clear)

    def clear(self):
        for group in self.groups():
            self.removeImgGroup(group)
        for buttonGroup in self.buttonGroups:
            buttonGroup.setExclusive(False)
        for radio_button in [self.radioButton, self.radioButton_2,
                             self.radioButton_3, self.radioButton_4,
                             self.radioButton_5, self.radioButton_6,
                             self.radioButton_7, self.radioButton_8]:
            radio_button.setChecked(False)
        for buttonGroup in self.buttonGroups:
            buttonGroup.setExclusive(True)
        for child in self.findChildren(QCheckBox):
            child.setChecked(False)
        for child in self.findChildren(QLineEdit):
            child.setText('')
        self.pushButton.setText('Click to set')

    def TestKeyEvent(self, event):
        self.pushButton.setDown(True)
        self.pushButton.setDisabled(True)
        self.pushButton.setStyleSheet("background-color: red;")
        self.settingtestkey = True

    def keyPressEvent(self, event: QKeyEvent) -> None:
        super().keyPressEvent(event)
        if self.settingtestkey:
            self.pushButton.setDown(False)
            self.pushButton.setDisabled(False)
            self.pushButton.setStyleSheet("background-color: none;")
            self.settingtestkey = False
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
                case default:
                    text = QKeySequence(key).toString()
            self.pushButton.setText(text)
            self.test_key_id = key

    def groups(self):
        return [self.verticalLayout.itemAt(i).widget() for i in range(self.verticalLayout.count() - 2)]

    def addImgGroupEvent(self, event):
        self.addImgGroup()

    def addImgGroup(self, images=[], name='', id=None, rate=1):
        if id == None:
            id = self.get_id()
        group = ImgGroupFrame(self, id, images, name)
        self.verticalLayout.insertWidget(
            self.verticalLayout.count() - 2, group)

    def removeImgGroup(self, group: ImgGroupFrame) -> None:
        group.hide()
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
        if self.verticalLayout.itemAt(hovering_index) is not None and self.verticalLayout.itemAt(hovering_index).widget().id != drag_cache['group'].id:
            group_id = drag_cache['group'].id
            name = drag_cache['group'].ui.lineEdit.text()
            pixmaps = [image.pixmap for image in drag_cache['group'].images()]
            ids = [image.id for image in drag_cache['group'].images()]
            files = [image.file for image in drag_cache['group'].images()]
            images = [ImgFrame(file, id, self, pixmap)
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

    def intergroup_show_order(self):
        widgets = list(filter(lambda x: x.isChecked(),
                              self.frame_4.findChildren(QRadioButton)))
        if widgets:
            return widgets[0].text()

    def intragroup_show_order(self):
        widgets = list(filter(lambda x: x.isChecked(),
                              self.frame_5.findChildren(QRadioButton)))
        if widgets:
            return widgets[0].text()

    def intergroup_behaviour(self):
        widgets = list(filter(lambda x: x.isChecked(),
                              self.frame_6.findChildren(QRadioButton)))
        if widgets:
            return widgets[0].text()

    def selection_rate_behaviour(self):
        widgets = list(filter(lambda x: x.isChecked(),
                              self.frame_7.findChildren(QRadioButton)))
        if widgets:
            return widgets[0].text()

    def allow_image_repetition(self):
        return self.checkBox_2.isChecked()

    def amount_of_exhibitions(self):
        text = self.lineEdit.text()
        if self.lineEdit.text():
            return int(text)
        else:
            return None

    def show_time(self):
        text = self.lineEdit_2.text()
        if self.lineEdit_2.text():
            return int(text)
        else:
            return None

    def interval_time(self):
        text = self.lineEdit_3.text()
        if self.lineEdit_3.text():
            return int(text)
        else:
            return None

    def test_key(self):
        return self.pushButton.text()

    def skip_on_click(self):
        return self.checkBox_3.isChecked()

    def get_configs(self):
        if isinstance(self.test_key_id, Qt.MouseButton):
            test_key_id = self.test_key_id.name
        elif isinstance(self.test_key_id, int):
            test_key_id = self.test_key_id
        elif isinstance(self.test_key_id, QPoint):
            test_key_id = (self.test_key_id.x(), self.test_key_id.y())
        else:
            test_key_id = None
        configs = {
            'groups': {group.id: group.get_configs() for group in self.groups()},
            'intergroup_show_order': self.intergroup_show_order(),
            'intragroup_show_order': self.intragroup_show_order(),
            'intergroup_behaviour': self.intergroup_behaviour(),
            'selection_rate_behaviour': self.selection_rate_behaviour(),
            'allow_image_repetition': self.allow_image_repetition(),
            'amount_of_exhibitions': self.amount_of_exhibitions(),
            'show_time': self.show_time(),
            'interval_time': self.interval_time(),
            'test_key': test_key_id,
            'skip_on_click': self.skip_on_click()
        }
        return configs

    def mousePressEvent(self, event: QMouseEvent) -> None:
        super().mousePressEvent(event)
        if self.settingtestkey:
            self.pushButton.setDown(False)
            self.pushButton.setDisabled(False)
            self.pushButton.setStyleSheet("background-color: none;")
            self.settingtestkey = False
            button = event.button()
            text = button.name
            self.pushButton.setText(text)
            self.test_key_id = button

    def wheelEvent(self, event: QWheelEvent) -> None:
        super().wheelEvent(event)
        if self.settingtestkey:
            self.pushButton.setDown(False)
            self.pushButton.setDisabled(False)
            self.pushButton.setStyleSheet("background-color: none;")
            self.settingtestkey = False
            if sign(event.angleDelta().y()) == 1:
                self.pushButton.setText('ScrollUp')
            else:
                self.pushButton.setText('ScrollDown')
            self.test_key_id = event.angleDelta()

    def make_default(self, event):
        platform = get_sys()
        if platform == 'linux':
            home_dir = Path(os.environ['HOME'])
        elif platform == 'windows':
            home_dir = Path(os.environ['HOMEDRIVE']) / \
                Path(os.environ['HOMEPATH'])
        else:
            raise OSError(
                'Stimulus is not entirely compatible with this operational system.')
        if not os.path.isdir(home_dir / '.Stimulus'):
            os.mkdir(home_dir / '.Stimulus')
        self.save_settings(home_dir/'.Stimulus/default.json')

    def save_settings(self, path):
        with open(path, 'w') as file:
            json.dump(self.get_configs(), file, indent=4)

    def load_settings(self, path):
        with open(path, 'r') as file:
            configs = json.load(file)

            # intergroup show order
            if configs['intergroup_show_order']:
                filter(lambda x: x.text() == configs['intergroup_show_order'],
                       self.frame_4.findChildren(QRadioButton)).__next__().setChecked(True)

            # intragroup show order
            if configs['intragroup_show_order']:
                filter(lambda x: x.text() == configs['intragroup_show_order'],
                       self.frame_5.findChildren(QRadioButton)).__next__().setChecked(True)

            # intergroup behaviour
            if configs['intergroup_behaviour']:
                filter(lambda x: x.text() == configs['intergroup_behaviour'],
                       self.frame_6.findChildren(QRadioButton)).__next__().setChecked(True)

            # selection rate behaviour
            if configs['selection_rate_behaviour']:
                filter(lambda x: x.text() == configs['selection_rate_behaviour'],
                       self.frame_7.findChildren(QRadioButton)).__next__().setChecked(True)

            # allow image repetition
            if configs['allow_image_repetition']:
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
            if configs['test_key']:
                if isinstance(configs['test_key'], int):
                    self.test_key_id = configs['test_key']
                    self.pushButton.setText(QKeySequence(
                        configs['test_key']).toString())
                elif isinstance(configs['test_key'], list):
                    self.test_key_id = QPoint(0, configs['test_key'][1])
                    if sign(self.test_key_id.y()) == 1:
                        self.pushButton.setText('ScrollUp')
                    else:
                        self.pushButton.setText('ScrollDown')
                else:
                    self.test_key_id = Qt.MouseButton[configs['test_key']]
                    self.pushButton.setText(configs['test_key'])

            # skip on click
            if configs['skip_on_click']:
                self.checkBox_3.setChecked(True)

            # images
            if configs['groups']:
                for group in configs['groups']:
                    images = [
                        ImgFrame(configs['groups'][group]['images'][i]['file'], i, rate=configs['groups'][group]['images'][i]['rate']) for i in configs['groups'][group]['images']
                    ]
                    self.addImgGroup(
                        images, configs['groups'][group]['name'], group, configs['groups'][group]['rate'])

    def load_default(self):
        platform = get_sys()
        if platform == 'linux':
            home_dir = Path(os.environ['HOME'])
        elif platform == 'windows':
            home_dir = Path(os.environ['HOMEDRIVE']) / \
                Path(os.environ['HOMEPATH'])
        else:
            return
        if os.path.isdir(home_dir/'.Stimulus'):
            if os.path.isfile(home_dir/'.Stimulus/default.json'):
                self.load_settings(home_dir/'.Stimulus/default.json')

    def saveSettingsEvent(self, event):
        path = QFileDialog.getSaveFileName(
            self, 'Save Settings', '', '*.json')
        if len(path) == 1:
            if not path.endswith('.json'):
                path += '.json'
            self.save_settings(path[0])

    def loadSettingsEvent(self, event):
        path = QFileDialog.getOpenFileName(
            self, 'Load Settings', '', '*.json')
        if len(path) == 1:
            for group in self.groups():
                self.removeImgGroup(group)
            self.load_settings(path[0])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Stimulus()
    window.show()
    app.exec()

# TODO: TIRAR VARIAVEIS GLOBAIS
# TODO: TIRAR VALORES HARD-CODED
# TODO: DEIXAR DICIONARIO COMO VARIAVEL NORMAL, DESFAZER DICIONARIO
# TODO: ADICIONAR CLEAR BUTTONS
