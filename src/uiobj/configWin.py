# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/kk/myproject/baidu-Sync-project/res/configWin.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(503, 279)
        self.lineEdit_2 = QtWidgets.QLineEdit(Form)
        self.lineEdit_2.setGeometry(QtCore.QRect(130, 20, 331, 31))
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(10, 20, 111, 31))
        self.label.setObjectName("label")
        self.lineEdit = QtWidgets.QLineEdit(Form)
        self.lineEdit.setGeometry(QtCore.QRect(90, 140, 301, 31))
        self.lineEdit.setReadOnly(True)
        self.lineEdit.setObjectName("lineEdit")
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(10, 140, 61, 31))
        self.label_2.setObjectName("label_2")
        self.pushButton_2 = QtWidgets.QPushButton(Form)
        self.pushButton_2.setGeometry(QtCore.QRect(280, 230, 81, 31))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(460, 20, 41, 31))
        self.pushButton.setObjectName("pushButton")
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setGeometry(QtCore.QRect(10, 230, 91, 31))
        self.label_3.setObjectName("label_3")
        self.comboBox = QtWidgets.QComboBox(Form)
        self.comboBox.setGeometry(QtCore.QRect(120, 230, 91, 31))
        self.comboBox.setEditable(False)
        self.comboBox.setObjectName("comboBox")
        self.label_4 = QtWidgets.QLabel(Form)
        self.label_4.setGeometry(QtCore.QRect(230, 230, 67, 31))
        self.label_4.setObjectName("label_4")
        self.pushButton_movedir = QtWidgets.QPushButton(Form)
        self.pushButton_movedir.setGeometry(QtCore.QRect(190, 60, 89, 31))
        self.pushButton_movedir.setObjectName("pushButton_movedir")
        self.pushButton_changremote = QtWidgets.QPushButton(Form)
        self.pushButton_changremote.setGeometry(QtCore.QRect(400, 140, 101, 31))
        self.pushButton_changremote.setObjectName("pushButton_changremote")
        self.line = QtWidgets.QFrame(Form)
        self.line.setGeometry(QtCore.QRect(0, 100, 501, 20))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.line_2 = QtWidgets.QFrame(Form)
        self.line_2.setGeometry(QtCore.QRect(0, 190, 501, 20))
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "设置"))
        self.label.setText(_translate("Form", "本地同步盘位置"))
        self.label_2.setText(_translate("Form", "远程目录 "))
        self.pushButton_2.setText(_translate("Form", " 应用"))
        self.pushButton.setText(_translate("Form", "..."))
        self.label_3.setText(_translate("Form", "自动同步时间"))
        self.label_4.setText(_translate("Form", "分钟"))
        self.pushButton_movedir.setText(_translate("Form", "移动同步盘"))
        self.pushButton_changremote.setText(_translate("Form", "修改远程目录"))
