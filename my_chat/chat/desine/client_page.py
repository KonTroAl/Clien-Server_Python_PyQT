# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'client_page.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ClientWindow(object):
    def setupUi(self, ClientWindow):
        ClientWindow.setObjectName("ClientWindow")
        ClientWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(ClientWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.ContactsList = QtWidgets.QTextEdit(self.centralwidget)
        self.ContactsList.setGeometry(QtCore.QRect(10, 160, 191, 391))
        self.ContactsList.setObjectName("ContactsList")
        self.FinderContacts = QtWidgets.QTextEdit(self.centralwidget)
        self.FinderContacts.setGeometry(QtCore.QRect(10, 100, 191, 31))
        self.FinderContacts.setObjectName("FinderContacts")
        self.HeddingContactsList = QtWidgets.QLabel(self.centralwidget)
        self.HeddingContactsList.setGeometry(QtCore.QRect(10, 140, 191, 20))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.HeddingContactsList.setFont(font)
        self.HeddingContactsList.setObjectName("HeddingContactsList")
        self.HeddingFinder = QtWidgets.QLabel(self.centralwidget)
        self.HeddingFinder.setGeometry(QtCore.QRect(10, 80, 191, 20))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.HeddingFinder.setFont(font)
        self.HeddingFinder.setObjectName("HeddingFinder")
        self.EnterMessage = QtWidgets.QTextEdit(self.centralwidget)
        self.EnterMessage.setGeometry(QtCore.QRect(230, 510, 451, 41))
        self.EnterMessage.setObjectName("EnterMessage")
        self.SendMessageButton = QtWidgets.QPushButton(self.centralwidget)
        self.SendMessageButton.setGeometry(QtCore.QRect(690, 510, 91, 41))
        self.SendMessageButton.setObjectName("SendMessageButton")
        self.UserLable = QtWidgets.QLabel(self.centralwidget)
        self.UserLable.setGeometry(QtCore.QRect(10, 30, 771, 31))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.UserLable.setFont(font)
        self.UserLable.setObjectName("UserLable")
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(230, 100, 551, 391))
        self.textBrowser.setObjectName("textBrowser")
        ClientWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(ClientWindow)
        self.SendMessageButton.clicked.connect(self.EnterMessage.clear)
        QtCore.QMetaObject.connectSlotsByName(ClientWindow)

    def retranslateUi(self, ClientWindow):
        _translate = QtCore.QCoreApplication.translate
        ClientWindow.setWindowTitle(_translate("ClientWindow", "ClientWindow"))
        self.FinderContacts.setPlaceholderText(_translate("ClientWindow", "Поиск"))
        self.HeddingContactsList.setText(_translate("ClientWindow", "Список контактов"))
        self.HeddingFinder.setText(_translate("ClientWindow", "Поиск/добавление контактов"))
        self.EnterMessage.setPlaceholderText(_translate("ClientWindow", "Введите ваше сообщение..."))
        self.SendMessageButton.setText(_translate("ClientWindow", "Отправить"))
        self.UserLable.setText(_translate("ClientWindow", "Test"))
