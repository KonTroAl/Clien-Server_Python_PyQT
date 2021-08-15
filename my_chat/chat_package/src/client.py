import sys
from queue import Queue
import datetime

from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

import importlib.util
import importlib

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from . import client_page
from . import my_server


timestamp = datetime.datetime.now()


engine = create_engine('sqlite:///sqlite3.db', echo=False, pool_recycle=7200)
Session = sessionmaker(bind=engine)
Session.configure(bind=engine)

session = Session()


class ContactsFinder:
    def __init__(self, user, res_queue):
        self.res_queue = res_queue
        self.user = user

    def find_contacts(self):
        id_user = session.query(my_server.Clients).filter_by(user_name=self.user).first()
        user_contact_id = session.query(my_server.ClientContacts).filter_by(id_owner=id_user.id).all()
        for i in user_contact_id:
            contact_name = session.query(my_server.Clients).filter_by(id=i.__dict__['id_client']).first()
            if self.res_queue is not None:
                self.res_queue.put(contact_name.user_name)
        if self.res_queue is not None:
            self.res_queue.put(None)


class ClientContactsView(QObject):
    gotData = pyqtSignal(list)

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.res_queue = Queue()
        self.find_contact = ContactsFinder(self.user, self.res_queue)

    def show_contacts(self):
        user_contacts = []
        self.find_contact.find_contacts()
        while True:
            data = self.res_queue.get()
            if data is None:
                break
            user_contacts.append(data)
            self.res_queue.task_done()
        self.res_queue.task_done()
        self.gotData.emit(user_contacts)
        return user_contacts


class ClientPage(QtWidgets.QDialog):
    def __init__(self, s, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = client_page.Ui_ClientWindow()
        self.ui.setupUi(self)
        self.ui.SendMessageButton.clicked.connect(self.send_message)
        self.ui.SearchButton.clicked.connect(self.add_contact)

        self.contacts_list = None
        self.s = s

    @pyqtSlot(list)
    def show_client_contacts(self, data):
        for i in data:
            self.ui.ContactsList.addItem(i)

    # def start_server(self):
    #     HOST = 'localhost'
    #     PORT = 7777
    #     client = my_client.Client()
    #     s = client.create_socket()
    #     client.start_connection(HOST, PORT, s)
    #     return s

    def send_message(self):
        """
        Без запуска приложения admin.py любая попытка отправить сообщение приведет к ошибке,
        т.к. сервер не будет запущен для обработки запроса пользователя
        """
        message = self.ui.EnterMessage.text()
        to = self.ui.ChatHedding.text()
        contact = session.query(my_server.Clients).filter_by(user_name=to).first()
        contact_id = contact.id
        user_lable = self.ui.UserLable.text()
        user = session.query(my_server.Clients).filter_by(user_name=user_lable).first()
        id_user = user.id
        if message:
            if to == 'ChatName':
                self.ui.textBrowser.append('Choose chat from contact list!')
            else:
                message_dict = {
                    'action': 'msg',
                    'time': timestamp,
                    'to': to,
                    'from': user,
                    'encoding': 'utf-8',
                    'message': message
                }
                """
                Нижняя строка пока будет закомментирована, 
                до реализации функционала авторизации пользователя на сервере 
                """
                add_message = my_server.ClientMessageHistory(id_user, contact_id, str(message), str(timestamp))
                session.add(add_message)
                session.commit()
                # self.s.send(pickle.dumps(message_dict))
                self.ui.textBrowser.append(f'{user} ({datetime.datetime.now()}): {message}')
        self.ui.EnterMessage.clear()

    def choose_contact(self, item):
        self.ui.ChatHedding.setText(item.text())

    def add_contact(self):
        user_name = self.ui.UserLable.text()
        user = session.query(my_server.Clients).filter_by(user_name=user_name).first()
        id_user = user.id
        contact_name = self.ui.FinderContacts.text()
        contact = session.query(my_server.Clients).filter_by(user_name=contact_name).first()
        contact_id = contact.id
        ContactList_items = self.ui.ContactsList
        items = []
        for i in range(ContactList_items.count()):
            items.append(ContactList_items.item(i).text())
        if id_user == contact_id or contact_name in items:
            print('Error!')
        else:
            add_contact = my_server.ClientContacts(id_user, contact_id)
            session.add(add_contact)
            session.commit()
            self.ui.ContactsList.addItem(contact_name)
        self.ui.FinderContacts.clear()

    def start_client(self, user_name):
        self.ui.UserLable.setText(user_name)
        self.contacts_list = ClientContactsView(self.ui.UserLable.text())
        self.contacts_list.gotData.connect(self.show_client_contacts)
        self.contacts_list.show_contacts()

        self.ui.SearchButton.setAutoDefault(True)
        self.ui.FinderContacts.returnPressed.connect(self.ui.SearchButton.click)

        self.ui.ContactsList.itemDoubleClicked.connect(self.choose_contact)

        # msg = Thread(target=my_client.message_recv, args=(self.s,))
        # msg.start()
        # while True:
        self.ui.SendMessageButton.setAutoDefault(True)
        self.ui.EnterMessage.returnPressed.connect(self.ui.SendMessageButton.click)
        # msg.join(timeout=1)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    client_page = ClientPage()
    # client_page.start_client('test')
    client_page.show()
    sys.exit(app.exec_())
