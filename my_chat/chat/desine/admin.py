from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal, pyqtSlot

from admin_panel_original import Ui_MainWindow
from HW.my_chat.chat import my_server


class AdminDialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.PortConnectionButton.clicked.connect(self.start_connection)
        self.ui.PortConnectionButton.clicked.connect(self.stop_connection)
        self.ui.DBConnectionButton.clicked.connect(self.start_db_connection)
        self.ui.DBConnectionButton.clicked.connect(self.stop_db_connection)

        self.is_active = False

    def start_connection(self):
        if not self.is_active:
            self.ui.ClientsList.clear()
            self.ui.ClientsStatistic.clear()
            self.is_active = True
            port = self.ui.PortTextBox.text()


            server = my_server.Server()
            server.start_server(port)
