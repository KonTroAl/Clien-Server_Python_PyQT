import sys

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
        self.ui.DBConnectionButton.clicked.connect(self.start_connection)
        # self.ui.PortConnectionButton.clicked.connect(self.stop_connection)
        # self.ui.DBConnectionButton.clicked.connect(self.start_db_connection)
        # self.ui.DBConnectionButton.clicked.connect(self.stop_db_connection)
        self.start = None
        self.start_db = False
        self.is_active = False


    def start_server(self):
        port = self.ui.PortTextBox.text()
        start = my_server.main(port)
        return start

    def start_DB(self):
        pass

    def start_connection(self):

        if not self.start_db:
            pass

        self.ui.PortConnectionButton.setEnabled(True)

        self.start_db = self.start_DB()

        self.start = self.start_server()
        self.thread = QThread()
        self.start.moveToThread(self.thread)

        self.thread.started.connect(self.start)

        self.thread.start()



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    admin = AdminDialog()
    admin.show()

    sys.exit(app.exec_())