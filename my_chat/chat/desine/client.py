import sys
from queue import Queue

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal, pyqtSlot

import importlib.util
import importlib

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from client_page import Ui_ClientWindow


def module_from_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


my_server = module_from_file('my_server', '../my_server.py')

engine = create_engine('sqlite:///../sqlite3.db', echo=True, pool_recycle=7200)
Session = sessionmaker(bind=engine)
Session.configure(bind=engine)

session = Session()


# print(session.query(my_server.Clients).all())

class ContactsFinder:
    def __init__(self, user):
        self.res_queue = Queue()
        self.user = user

    def find_contacts(self):
        # user_contact = []
        id_user = session.query(my_server.Clients).filter_by(user_name=self.user).first()
        user_contact_id = session.query(my_server.ClientContacts).filter_by(id_owner=id_user.id).all()
        for i in user_contact_id:
            contact_name = session.query(my_server.Clients).filter_by(id=i.__dict__['id_client']).first()
            if self.res_queue is not None:
                self.res_queue.put(contact_name.user_name)
        if self.res_queue is not None:
            self.res_queue.put(None)
            self.res_queue.join()
            # self.gotData.emit(contact_name.user_name)
            # user_contact.append(contact_name.user_name)
        # self.finished.emit(0)
        # return user_contact


class ClientContactsView(QObject):
    gotData = pyqtSignal(str)
    finished = pyqtSignal(int)

    def __init__(self, user):
        super(ClientContactsView, self).__init__(user)
        self.user = user
        self.find_contact = ContactsFinder(self.user)

    def show_contacts(self):
        self.find_contact.find_contacts()
        while True:
            data = self.res_queue.get()
            if data is None:
                break
            self.gotData.emit(data)
            self.res_queue.task_done()
        self.res_queue.task_done()
        self.finished.emit(0)


class ClientPage(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = Ui_ClientWindow()
        self.ui.setupUi(self)
        self.ui.SendMessageButton.clicked.connect(self.send_message)
        self.contacts_list = None

    @pyqtSlot(str)
    def show_client_contacts(self, data):
        self.ui.ContactsList.appendPlainText(data)
        # for text in data[1]:
        #     self.ui.ContactsList.appendPlainText(" " + text)
        self.ui.ContactsList.appendPlainText("")

    def send_message(self):
        pass

    def start_client(self):
        self.contacts_list = ClientContactsView('test')
        self.contacts_list.gotData.connect(self.show_client_contacts)


if __name__ == '__main__':
    test_val = ClientContactsView('test')
    print(test_val.show_contacts())
    app = QtWidgets.QApplication(sys.argv)
    client_page = ClientPage()
    client_page.show()
    sys.exit(app.exec_())
    # my_server.main()
