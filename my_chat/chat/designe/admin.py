import sys
import multiprocessing
from threading import Thread

from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal, pyqtSlot

import importlib.util
import importlib

from admin_panel import Ui_MainWindow


def module_from_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


my_server = module_from_file('my_server', '../my_server.py')


class AdminDialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.PortConnectionButton.clicked.connect(self.start_connection)
        self.ui.PortConnectionButton.setEnabled(False)
        self.ui.DBConnectionButton.clicked.connect(self.start_connection)

        self.start = None
        self.start_db = False

    def start_server(self):
        port = self.ui.PortTextBox.text()
        start = my_server.main(port)

        return start

    def start_DB(self):
        dialect = self.ui.DialectDBTextBox.text()
        name_db = self.ui.NameDBTextBox.text()
        session = my_server.main_db(dialect, name_db)
        return session

    def start_connection(self):

        self.start = Thread(target=self.start_server)
        self.start.daemon = True
        self.start.start()

        self.start_db = self.start_DB()
        self.ui.PortConnectionButton.setEnabled(True)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    admin = AdminDialog()
    admin.show()

    sys.exit(app.exec_())
