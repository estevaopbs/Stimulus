from pathlib import Path
from PyQt6.QtCore import Qt, QUrl, QMimeData, QSize, QPoint, QThread
from numpy import sign
from qt_templates.ImgGroup.ImgGroup import Ui_Frame as ImgGroup
from qt_templates.MainWindow.MainWindow import Ui_MainWindow as MainWindow
from PyQt6.QtWidgets import QMainWindow, QApplication, QFrame, QFileDialog, QRadioButton, QLineEdit, QCheckBox, QButtonGroup, QMessageBox
from PyQt6.QtGui import QPixmap, QDrag, QPainter, QScreen, QIntValidator, QKeyEvent, QKeySequence, QMouseEvent, QWheelEvent
from qt_templates.Img.Img import Ui_Form as Img
import sys
import os
import imghdr
from math import floor
import json
from select_images import SelectImages
from itertools import chain
from show import ShowWindow
from multiprocessing import Process


drag_cache = None


def get_id(n=0):
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
        self.ui.spinBox.setRange(1, 999999)
        self.ui.spinBox.setValue(rate)

    def group_name(self):
        return self.master.name

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
        if self != master_images[-1]:
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
        self.ui.spinBox.setRange(1, 999999)
        self.ui.spinBox.setValue(1)

    def rate(self) -> int:
        return self.ui.spinBox.value()

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
            self.addImg(ImgFrame(file.url().replace(
                'file://', ''), self.master.get_id(), self))

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
                0, ImgFrame(drag_cache['img'].file, drag_cache['img'].id, self, drag_cache['img'].pixmap, drag_cache['img'].rate()))
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
                hovering_index, ImgFrame(drag_cache['img'].file, drag_cache['img'].id, self, drag_cache['img'].pixmap, drag_cache['img'].rate()))

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


class Stimulus(QMainWindow, MainWindow):
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
        self.settinginteractionkey = False
        self.interaction_key_id = None
        self.pushButton.clicked.connect(self.InteractionKeyEvent)
        self.pushButton.wheelEvent = self.wheelEvent
        self.pushButton_5.clicked.connect(self.make_default)
        for lineEdit in self.findChildren(QLineEdit):
            lineEdit.setValidator(self.onlyInt)
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
        self.buttonGroup_3.addButton(self.radioButton_9)
        self.buttonGroup_4.addButton(self.radioButton_7)
        self.buttonGroup_4.addButton(self.radioButton_8)
        self.buttonGroups = [self.buttonGroup, self.buttonGroup_2,
                             self.buttonGroup_3, self.buttonGroup_4]
        self.pushButton_2.clicked.connect(self.saveSettingsEvent)
        self.pushButton_3.clicked.connect(self.loadSettingsEvent)
        self.pushButton_7.clicked.connect(self.clear)
        for screen in QApplication.screens():
            self.comboBox.addItem(screen.name())
        self.pushButton_4.clicked.connect(self.startEvent)
        self.load_default()

    def clear(self):
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
        for child in self.findChildren(QCheckBox):
            child.setChecked(False)
        for child in self.findChildren(QLineEdit):
            child.setText('')
        self.pushButton.setText('Click to set')

    def InteractionKeyEvent(self, event):
        self.pushButton.setDown(True)
        self.pushButton.setDisabled(True)
        self.pushButton.setStyleSheet("background-color: red;")
        self.settinginteractionkey = True

    def keyPressEvent(self, event: QKeyEvent) -> None:
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
                    text = QKeySequence(key).toString()
            self.pushButton.setText(text)
            self.interaction_key_id = key

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

    def allow_image_repeat(self):
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

    def interaction_key(self):
        return self.pushButton.text()

    def skip_on_click(self):
        return self.checkBox_3.isChecked()

    def screen_(self):
        return self.comboBox.currentText()

    def get_configs(self):
        if isinstance(self.interaction_key_id, Qt.MouseButton):
            interaction_key_id = self.interaction_key_id.name
        elif isinstance(self.interaction_key_id, int):
            interaction_key_id = self.interaction_key_id
        elif isinstance(self.interaction_key_id, QPoint):
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

    def mousePressEvent(self, event: QMouseEvent) -> None:
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

    def wheelEvent(self, event: QWheelEvent) -> None:
        super().wheelEvent(event)
        if self.settinginteractionkey:
            self.pushButton.setDown(False)
            self.pushButton.setDisabled(False)
            self.pushButton.setStyleSheet("background-color: none;")
            self.settinginteractionkey = False
            if sign(event.angleDelta().y()) == 1:
                self.pushButton.setText('ScrollUp')
            else:
                self.pushButton.setText('ScrollDown')
            self.interaction_key_id = event.angleDelta()

    def make_default(self, event):
        home_dir = Path.home()
        if not os.path.isdir(home_dir / '.Stimulus'):
            os.mkdir(home_dir / '.Stimulus')
        self.save_settings(home_dir/'.Stimulus/default.json')

    def save_settings(self, path):
        with open(path, 'w') as file:
            json.dump(self.get_configs(), file, indent=4)

    def load_settings(self, path):
        with open(path, 'r') as file:
            configs = json.load(file)

            # ids generator
            self.ids_generator = get_id(configs['n'] + 1)

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
                    self.pushButton.setText(QKeySequence(
                        configs['interaction_key']).toString())
                elif isinstance(configs['interaction_key'], list):
                    self.interaction_key_id = QPoint(
                        0, configs['interaction_key'][1])
                    if sign(self.interaction_key_id.y()) == 1:
                        self.pushButton.setText('ScrollUp')
                    else:
                        self.pushButton.setText('ScrollDown')
                else:
                    self.interaction_key_id = Qt.MouseButton[configs['interaction_key']]
                    self.pushButton.setText(configs['interaction_key'])

            # skip on click
            if configs['skip_on_click']:
                self.checkBox_3.setChecked(True)

            # images
            if configs['groups']:
                for group in configs['groups']:
                    images = [
                        ImgFrame(configs['groups'][group]['images'][i]['file'], int(i), rate=configs['groups'][group]['images'][i]['rate']) for i in configs['groups'][group]['images']
                    ]
                    self.addImgGroup(
                        images, configs['groups'][group]['name'], int(group), configs['groups'][group]['rate'])

    def load_default(self):
        home_dir = Path.home()
        if os.path.isdir(home_dir/'.Stimulus'):
            if os.path.isfile(home_dir/'.Stimulus/default.json'):
                self.load_settings(home_dir/'.Stimulus/default.json')

    def saveSettingsEvent(self, event):
        path = QFileDialog.getSaveFileName(
            self, 'Save Settings', '', '*.json')
        if len(path) > 0:
            path = path[0]
            if not path.endswith('.json'):
                path += '.json'
            self.save_settings(path)

    def loadSettingsEvent(self, event):
        path = QFileDialog.getOpenFileName(
            self, 'Load Settings', '', '*.json')
        if len(path) > 0:
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
        if not self.interval_time():
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
            QMessageBox.warning(self, 'Error', text)
            return False
        return True

    def startEvent(self, event):
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
                    'file': image.file,
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
    app = QApplication(sys.argv)
    window = Stimulus()
    window.show()
    app.exec()

# TODO: TIRAR VARIAVEIS GLOBAIS
# TODO: TIRAR VALORES HARD-CODED
# TODO: DEIXAR DICIONARIO COMO VARIAVEL NORMAL, DESFAZER DICIONARIO
# TODO: DEIXAR O CODIGO MAIS LIMPO
# TODO: FAZER CLASSES COM HERANÇA
# TODO: CONSERTAR TAB
# TODO: ADICIONAR SUPORTE PRA TELA SECUNDÁRIA
# TODO: ESTILIZAÇÂO COM CSS
# TODO: MUDAR NOME DO SCROLL NAS SAVE FILES
# TODO: ADICIONAR SUPORTE AS TECLAS DIRECIONAIS
# TODO: AUMENTAR O TAMANHO DO FRAME ESQUERDO QUANDO APARECER A SCROLLBAR
# TODO: PERMITIR RATE = 0
# TODO: JANELA DE MONITORAMENTO
