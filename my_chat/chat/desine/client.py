import sys
from queue import Queue
from threading import Thread

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
    def __init__(self, user, res_queue):
        self.res_queue = res_queue
        self.user = user
        # self.is_alive = False

    def find_contacts(self):
        # self.is_alive = True
        id_user = session.query(my_server.Clients).filter_by(user_name=self.user).first()
        user_contact_id = session.query(my_server.ClientContacts).filter_by(id_owner=id_user.id).all()
        for i in user_contact_id:
            # if not self.is_alive:
            #     break
            contact_name = session.query(my_server.Clients).filter_by(id=i.__dict__['id_client']).first()
            if self.res_queue is not None:
                self.res_queue.put(contact_name.user_name)
        # self.is_alive = False
        if self.res_queue is not None:
            self.res_queue.put(None)
            # self.res_queue.join()

    # def search_contacts(self):
    #     t = Thread(target=self.find_contacts())
    #     t.daemon = True
    #     t.start()


class ClientContactsView(QObject):
    gotData = pyqtSignal(tuple)
    finished = pyqtSignal(int)

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.res_queue = Queue()
        self.find_contact = ContactsFinder(self.user, self.res_queue)

    def show_contacts(self):
        self.find_contact.find_contacts()
        while True:
            data = self.res_queue.get()
            if data is None:
                break
            print(data)
            self.gotData.emit((data, ))
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

    @pyqtSlot(tuple)
    def show_client_contacts(self, data):
        for text in data:
            print(text)
            self.ui.ContactsList.insertPlainText(" " + text)
        self.ui.ContactsList.setPlainText("")

    def send_message(self):
        pass

    def start_client(self):
        # self.show_client_contacts()
        self.contacts_list = ClientContactsView(('test'))
        self.contacts_list.gotData.connect(self.show_client_contacts)
        # print(self.contacts_list.gotData)
        #
        self.thread = QThread()
        self.contacts_list.moveToThread(self.thread)

        self.thread.started.connect(self.contacts_list.show_contacts)
        self.contacts_list.finished.connect(self.thread.quit)
        self.contacts_list.finished.connect(self.finished)

        self.thread.start()


if __name__ == '__main__':
    # test_val = ClientPage()
    # test_val.start_client()
    app = QtWidgets.QApplication(sys.argv)
    client_page = ClientPage()
    client_page.show()
    sys.exit(app.exec_())
    # my_server.main()
