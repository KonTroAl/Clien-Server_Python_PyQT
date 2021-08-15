import sys
from threading import Thread

from PyQt5 import QtWidgets

import importlib.util
import importlib
import auth

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

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

        self.start = None
        self.start_db = False

    def start_DB(self):
        dialect = self.ui.DialectDBComboBox.currentText()
        name_db = self.ui.NameDBTextBox.text()
        engine = create_engine(f'{dialect}:///../{name_db}', echo=False, pool_recycle=7200)
        Session = sessionmaker(bind=engine)
        Session.configure(bind=engine)
        session = Session()
        return session


    def start_server(self):
        session = self.start_DB()
        port = self.ui.PortTextBox.text()
        start = my_server.main(port, session)
        return start

    def show_clients(self, session):
        clients = session.query(my_server.Clients).all()
        for client in clients:
            self.ui.ClientsList.append(str(client))

    def show_clients_statistic(self, session):
        clients = session.query(my_server.Clients).all()
        for client in clients:
            user = session.query(my_server.Clients).filter_by(user_name=client.__dict__['user_name']).first()
            user_id = user.id
            client_history = session.query(my_server.ClientHistory).filter_by(user_id=user_id).first()
            self.ui.ClientsStatistic.append(str(client_history))

    def start_connection(self):

        self.start = Thread(target=self.start_server)
        self.start.daemon = True
        self.start.start()

        self.start_db = self.start_DB()

        self.show_clients(self.start_db)
        self.show_clients_statistic(self.start_db)
        self.start.join(timeout=1)
        auth.show()



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    admin = AdminDialog()
    auth = auth.AuthPage()
    admin.show()
    sys.exit(app.exec_())
