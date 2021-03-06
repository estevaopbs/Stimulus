from __future__ import annotations
from typing import Any
from PyQt6 import QtGui, QtCore, QtWidgets
from templates.Show.Show import Ui_MainWindow as Show
from datetime import datetime
import time
import json


class ShowWindow(QtWidgets.QMainWindow, Show):
    def __init__(self, master: Stimulus, images: list[dict[str, Any]],
                 show_time: int, interval_time: int,
                 interaction_key: QtCore.QPoint | QtCore.Qt.MouseButton | int,
                 skip_on_click: bool, screen: str,
                 parent: None = None) -> None:
        super(ShowWindow, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Show")
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint |
                            QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.showFullScreen()
        self.master = master
        self.images = images
        self.show_time = show_time / 1000
        self.interval_time = interval_time / 1000
        self.interaction_key = interaction_key
        self.screen_ = next(filter(lambda x: x.name() == screen,
                            QtWidgets.QApplication.screens()))
        self.label.setStyleSheet("background-color: black;")
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.black_screen = QtGui.QPixmap(self.screen_.size())
        self.black_screen.fill(QtCore.Qt.GlobalColor.black)
        if type(interaction_key) == QtCore.QPoint:
            self.wheelEvent = self.scrollInteractionEvent
        elif type(interaction_key) == QtCore.Qt.MouseButton:
            self.mousePressEvent = self.mouseInteractionEvent
        else:
            self.keyPressEvent = self.keyInteractionEvent
        if skip_on_click:
            self.interactionEvent = self.skipEvent
        else:
            self.interactionEvent = self._interactionEvent
        self.times: list[float] = []
        self.relative_times: list[float] = []
        self.clicked_images: list[int] = []
        self.clicked = False
        self.skip = False
        self.running = False
        self.showing_image = False
        monitor = self.screen_.geometry()
        self.move(monitor.topLeft())
        self.resize(monitor.width(), monitor.height())
        self.setCursor(QtCore.Qt.CursorShape.BlankCursor)
        self.show()

    def run(self) -> None:
        self.running = True
        self.absolute_start_time = time.time()
        for n, image in enumerate(self.images):
            self.current_image = image
            self.relative_start_time = time.time()
            self.label.setPixmap(self.black_screen)
            self.showing_image = False
            while time.time() - self.relative_start_time < self.interval_time:
                QtWidgets.QApplication.processEvents()
            self.label.setPixmap(image['pixmap'].scaled(self.label.size(
            ), QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation))
            self.showing_image = True
            while time.time() - self.relative_start_time < self.interval_time + self.show_time and not self.skip:
                QtWidgets.QApplication.processEvents()
            if self.clicked:
                self.clicked_images.append(n)
            self.skip = False
            self.clicked = False
        self.running = False
        self.close()
        self.showReportBox()

    def scrollInteractionEvent(self, event: QtGui.QWheelEvent) -> None:
        if event.angleDelta() == self.interaction_key:
            if self.showing_image:
                self.interactionEvent()
                return
            elif not self.running:
                self.run()

    def mouseInteractionEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == self.interaction_key:
            if self.showing_image:
                self.interactionEvent()
            elif not self.running:
                self.run()

    def keyInteractionEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == self.interaction_key:
            if self.showing_image:
                self.interactionEvent()
                return
            elif not self.running:
                self.run()

    def skipEvent(self) -> None:
        self.skip = True
        self._interactionEvent()

    def _interactionEvent(self) -> None:
        if not self.clicked:
            now = time.time()
            self.times.append(now - self.absolute_start_time)
            self.relative_times.append(
                now - self.relative_start_time - self.interval_time)
            self.clicked = True

    def get_report(self) -> dict[str, Any]:
        report = {
            'id': self.id,
            'images': [
                {
                    'file': image['file'],
                    'group': image['group_name'],
                }
                for image in self.images
            ],
            'times': self.times,
            'relative_times': self.relative_times,
            'clicked_images': self.clicked_images,
            'datetime': datetime.strftime(datetime.now(), '%d/%m/%Y %H:%M:%S'),
            'show_time': self.show_time * 1000,
            'interval_time': self.interval_time * 1000
        }
        return report

    def showReportBox(self) -> None:
        report_box = QtWidgets.QMessageBox()
        report_box.setWindowTitle("Report")
        groups = set([image['group_name'] for image in self.images])
        groups_count = dict()
        for group in groups:
            groups_count[group] = 0
        for image in self.images:
            groups_count[image['group_name']] += 1
        clicked_groups_counts = dict()
        for group in groups:
            clicked_groups_counts[group] = 0
        for index in self.clicked_images:
            clicked_groups_counts[self.images[index]['group_name']] += 1
        image_ps = 'image was' if len(self.images) == 1 else 'images were'
        text = f"{len(self.images)} {image_ps} were exhibited of which\n"
        for group in groups:
            group_count_ps = 'was' if groups_count[group] == 1 else 'were'
            text += f'{groups_count[group]} {group_count_ps} from the group {group}\n'
        text += f"{len(self.clicked_images)} images were interacted of which\n"
        for group in groups:
            group_clicked_ps = 'was' if clicked_groups_counts[group] == 1 else 'were'
            text += f'{clicked_groups_counts[group]} {group_clicked_ps} from the group {group}\n'
        report_box.setText(text)
        report_box.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Save |
                                      QtWidgets.QMessageBox.StandardButton.Discard)
        btn = report_box.exec()
        if btn == QtWidgets.QMessageBox.StandardButton.Save:
            self.save_report()
        elif btn == QtWidgets.QMessageBox.StandardButton.Discard:
            pass

    def save_report(self) -> None:
        path = QtWidgets.QFileDialog.getSaveFileName(
            self, 'Save Data Report', '', 'JSON (*.json)')[0]
        if path:
            self.id = path.split('/')[-1].split('.')[0]
            if not path.endswith('.json'):
                path += '.json'
            with open(path, 'w') as f:
                json.dump(self.get_report(), f, indent=4)
