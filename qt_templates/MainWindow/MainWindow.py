# Form implementation generated from reading ui file 'MainWindow.ui'
#
# Created by: PyQt6 UI code generator 6.3.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(926, 835)
        MainWindow.setMinimumSize(QtCore.QSize(800, 300))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea.setMinimumSize(QtCore.QSize(260, 0))
        self.scrollArea.setMaximumSize(QtCore.QSize(260, 16777215))
        self.scrollArea.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 263, 817))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.gridLayout = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButton_2 = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 2, 0, 1, 1)
        self.pushButton_3 = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.pushButton_3.setObjectName("pushButton_3")
        self.gridLayout.addWidget(self.pushButton_3, 2, 1, 1, 1)
        self.frame_3 = QtWidgets.QFrame(self.scrollAreaWidgetContents)
        self.frame_3.setMaximumSize(QtCore.QSize(16777215, 25))
        self.frame_3.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.frame_3.setAutoFillBackground(False)
        self.frame_3.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame_3.setObjectName("frame_3")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_3)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pushButton_4 = QtWidgets.QPushButton(self.frame_3)
        self.pushButton_4.setMaximumSize(QtCore.QSize(80, 25))
        self.pushButton_4.setObjectName("pushButton_4")
        self.horizontalLayout_2.addWidget(self.pushButton_4)
        self.gridLayout.addWidget(self.frame_3, 3, 0, 1, 2)
        self.frame_7 = QtWidgets.QFrame(self.scrollAreaWidgetContents)
        self.frame_7.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame_7.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame_7.setObjectName("frame_7")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.frame_7)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.lineEdit = QtWidgets.QLineEdit(self.frame_7)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout_5.addWidget(self.lineEdit, 7, 1, 1, 1)
        self.lineEdit_3 = QtWidgets.QLineEdit(self.frame_7)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.gridLayout_5.addWidget(self.lineEdit_3, 9, 1, 1, 1)
        self.frame_9 = QtWidgets.QFrame(self.frame_7)
        self.frame_9.setMaximumSize(QtCore.QSize(16777215, 25))
        self.frame_9.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.frame_9.setAutoFillBackground(False)
        self.frame_9.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.frame_9.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame_9.setObjectName("frame_9")
        self.gridLayout_8 = QtWidgets.QGridLayout(self.frame_9)
        self.gridLayout_8.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.pushButton_5 = QtWidgets.QPushButton(self.frame_9)
        self.pushButton_5.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.pushButton_5.setObjectName("pushButton_5")
        self.gridLayout_8.addWidget(self.pushButton_5, 0, 0, 1, 1)
        self.pushButton_7 = QtWidgets.QPushButton(self.frame_9)
        self.pushButton_7.setObjectName("pushButton_7")
        self.gridLayout_8.addWidget(self.pushButton_7, 0, 1, 1, 1)
        self.gridLayout_5.addWidget(self.frame_9, 12, 0, 1, 2)
        self.label_2 = QtWidgets.QLabel(self.frame_7)
        self.label_2.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.label_2.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout_5.addWidget(self.label_2, 0, 0, 1, 2)
        self.frame_8 = QtWidgets.QFrame(self.frame_7)
        self.frame_8.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame_8.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame_8.setObjectName("frame_8")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.frame_8)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.radioButton_7 = QtWidgets.QRadioButton(self.frame_8)
        self.radioButton_7.setObjectName("radioButton_7")
        self.gridLayout_6.addWidget(self.radioButton_7, 1, 0, 1, 1)
        self.radioButton_8 = QtWidgets.QRadioButton(self.frame_8)
        self.radioButton_8.setAutoFillBackground(False)
        self.radioButton_8.setObjectName("radioButton_8")
        self.gridLayout_6.addWidget(self.radioButton_8, 1, 1, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.frame_8)
        self.label_10.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_10.setObjectName("label_10")
        self.gridLayout_6.addWidget(self.label_10, 0, 0, 1, 2)
        self.gridLayout_5.addWidget(self.frame_8, 4, 0, 1, 2)
        self.frame_5 = QtWidgets.QFrame(self.frame_7)
        self.frame_5.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame_5.setObjectName("frame_5")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.frame_5)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.radioButton_3 = QtWidgets.QRadioButton(self.frame_5)
        self.radioButton_3.setObjectName("radioButton_3")
        self.gridLayout_3.addWidget(self.radioButton_3, 1, 0, 1, 1)
        self.radioButton_4 = QtWidgets.QRadioButton(self.frame_5)
        self.radioButton_4.setObjectName("radioButton_4")
        self.gridLayout_3.addWidget(self.radioButton_4, 1, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.frame_5)
        self.label_4.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.gridLayout_3.addWidget(self.label_4, 0, 0, 1, 2)
        self.gridLayout_5.addWidget(self.frame_5, 2, 0, 1, 2)
        self.pushButton = QtWidgets.QPushButton(self.frame_7)
        self.pushButton.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout_5.addWidget(self.pushButton, 10, 1, 1, 1)
        self.frame_4 = QtWidgets.QFrame(self.frame_7)
        self.frame_4.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame_4.setObjectName("frame_4")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.frame_4)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.radioButton = QtWidgets.QRadioButton(self.frame_4)
        self.radioButton.setObjectName("radioButton")
        self.gridLayout_2.addWidget(self.radioButton, 1, 0, 1, 1)
        self.radioButton_2 = QtWidgets.QRadioButton(self.frame_4)
        self.radioButton_2.setObjectName("radioButton_2")
        self.gridLayout_2.addWidget(self.radioButton_2, 1, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.frame_4)
        self.label_3.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 0, 0, 1, 2)
        self.gridLayout_5.addWidget(self.frame_4, 1, 0, 1, 2)
        self.frame_6 = QtWidgets.QFrame(self.frame_7)
        self.frame_6.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame_6.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame_6.setObjectName("frame_6")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.frame_6)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.radioButton_6 = QtWidgets.QRadioButton(self.frame_6)
        self.radioButton_6.setAutoFillBackground(False)
        self.radioButton_6.setObjectName("radioButton_6")
        self.gridLayout_4.addWidget(self.radioButton_6, 2, 0, 1, 1)
        self.radioButton_5 = QtWidgets.QRadioButton(self.frame_6)
        self.radioButton_5.setObjectName("radioButton_5")
        self.gridLayout_4.addWidget(self.radioButton_5, 1, 0, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.frame_6)
        self.label_5.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_5.setObjectName("label_5")
        self.gridLayout_4.addWidget(self.label_5, 0, 0, 1, 1)
        self.radioButton_9 = QtWidgets.QRadioButton(self.frame_6)
        self.radioButton_9.setObjectName("radioButton_9")
        self.gridLayout_4.addWidget(self.radioButton_9, 3, 0, 1, 1)
        self.gridLayout_5.addWidget(self.frame_6, 3, 0, 1, 2)
        self.checkBox_3 = QtWidgets.QCheckBox(self.frame_7)
        self.checkBox_3.setObjectName("checkBox_3")
        self.gridLayout_5.addWidget(self.checkBox_3, 11, 0, 1, 2)
        self.label_6 = QtWidgets.QLabel(self.frame_7)
        self.label_6.setObjectName("label_6")
        self.gridLayout_5.addWidget(self.label_6, 7, 0, 1, 1)
        self.frame_10 = QtWidgets.QFrame(self.frame_7)
        self.frame_10.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame_10.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame_10.setObjectName("frame_10")
        self.gridLayout_10 = QtWidgets.QGridLayout(self.frame_10)
        self.gridLayout_10.setObjectName("gridLayout_10")
        self.label_12 = QtWidgets.QLabel(self.frame_10)
        self.label_12.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_12.setObjectName("label_12")
        self.gridLayout_10.addWidget(self.label_12, 0, 0, 1, 1)
        self.comboBox = QtWidgets.QComboBox(self.frame_10)
        self.comboBox.setObjectName("comboBox")
        self.gridLayout_10.addWidget(self.comboBox, 1, 0, 1, 1)
        self.gridLayout_5.addWidget(self.frame_10, 5, 0, 1, 2)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.frame_7)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.gridLayout_5.addWidget(self.lineEdit_2, 8, 1, 1, 1)
        self.checkBox_2 = QtWidgets.QCheckBox(self.frame_7)
        self.checkBox_2.setObjectName("checkBox_2")
        self.gridLayout_5.addWidget(self.checkBox_2, 6, 0, 1, 2)
        self.label_8 = QtWidgets.QLabel(self.frame_7)
        self.label_8.setObjectName("label_8")
        self.gridLayout_5.addWidget(self.label_8, 9, 0, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.frame_7)
        self.label_9.setObjectName("label_9")
        self.gridLayout_5.addWidget(self.label_9, 10, 0, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.frame_7)
        self.label_7.setObjectName("label_7")
        self.gridLayout_5.addWidget(self.label_7, 8, 0, 1, 1)
        self.gridLayout.addWidget(self.frame_7, 1, 0, 1, 2)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.gridLayout.addItem(spacerItem, 4, 0, 1, 2)
        self.label = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.horizontalLayout.addWidget(self.scrollArea)
        self.scrollArea_2 = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea_2.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.scrollArea_2.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollArea_2.setObjectName("scrollArea_2")
        self.scrollAreaWidgetContents_2 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_2.setGeometry(QtCore.QRect(0, 0, 642, 817))
        self.scrollAreaWidgetContents_2.setObjectName("scrollAreaWidgetContents_2")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents_2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtWidgets.QFrame(self.scrollAreaWidgetContents_2)
        self.frame.setMinimumSize(QtCore.QSize(0, 25))
        self.frame.setMaximumSize(QtCore.QSize(16777215, 25))
        self.frame.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.frame)
        self.gridLayout_7.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.pushButton_6 = QtWidgets.QPushButton(self.frame)
        self.pushButton_6.setMinimumSize(QtCore.QSize(30, 25))
        self.pushButton_6.setMaximumSize(QtCore.QSize(30, 25))
        self.pushButton_6.setObjectName("pushButton_6")
        self.gridLayout_7.addWidget(self.pushButton_6, 0, 1, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.gridLayout_7.addItem(spacerItem1, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.frame)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_2)
        self.horizontalLayout.addWidget(self.scrollArea_2)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton_2.setText(_translate("MainWindow", "Save settings"))
        self.pushButton_3.setText(_translate("MainWindow", "Load settings"))
        self.pushButton_4.setText(_translate("MainWindow", "Start"))
        self.pushButton_5.setText(_translate("MainWindow", "Make default"))
        self.pushButton_7.setText(_translate("MainWindow", "Clear"))
        self.label_2.setText(_translate("MainWindow", "Settings"))
        self.radioButton_7.setText(_translate("MainWindow", "Deterministic"))
        self.radioButton_8.setText(_translate("MainWindow", "Probabilistic"))
        self.label_10.setText(_translate("MainWindow", "Selection rate behaviour"))
        self.radioButton_3.setText(_translate("MainWindow", "Random"))
        self.radioButton_4.setText(_translate("MainWindow", "Sequential"))
        self.label_4.setText(_translate("MainWindow", "Intragroup show order"))
        self.pushButton.setText(_translate("MainWindow", "Click to set"))
        self.radioButton.setText(_translate("MainWindow", "Random"))
        self.radioButton_2.setText(_translate("MainWindow", "Sequential"))
        self.label_3.setText(_translate("MainWindow", "Intergroup show order"))
        self.radioButton_6.setText(_translate("MainWindow", "Select a new group on depletion\n"
"of the current"))
        self.radioButton_5.setText(_translate("MainWindow", "Select a new group on each show"))
        self.label_5.setText(_translate("MainWindow", "Intergroup behaviour"))
        self.radioButton_9.setText(_translate("MainWindow", "Select a new group once all\n"
"images have been shown"))
        self.checkBox_3.setText(_translate("MainWindow", "Skip on click"))
        self.label_6.setText(_translate("MainWindow", "Amount of exhibitions"))
        self.label_12.setText(_translate("MainWindow", "Screen"))
        self.checkBox_2.setText(_translate("MainWindow", "Allow image repeat"))
        self.label_8.setText(_translate("MainWindow", "Interval time (ms)"))
        self.label_9.setText(_translate("MainWindow", "Interaction key"))
        self.label_7.setText(_translate("MainWindow", "Show time (ms)"))
        self.label.setText(_translate("MainWindow", "STIMULUS"))
        self.pushButton_6.setText(_translate("MainWindow", "+"))
