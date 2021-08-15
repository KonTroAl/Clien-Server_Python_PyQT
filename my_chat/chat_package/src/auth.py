import sys
import os
import hashlib
import hmac
import datetime
import pickle
from time import sleep

from PyQt5 import QtWidgets

import importlib.util
import importlib

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from . import auth_page
from . import client
from . import my_client


admin_dict = {
    'login': 'admin',
    'password': 'admin'
}

secret_key = b'test_test'


engine = create_engine('sqlite:///sqlite3.db', echo=False, pool_recycle=7200)
Session = sessionmaker(bind=engine)
Session.configure(bind=engine)

session = Session()


def start_server():
    HOST = 'localhost'
    PORT = 7777
    client = my_client.Client()
    s = client.create_socket()
    client.start_connection(HOST, PORT, s)
    return s


class AuthPage(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = auth_page.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.SubmitButton.clicked.connect(self.client_auth)

    def client_auth(self):
        login = self.ui.LoginBox.text()
        password = self.ui.PasswordBox.text()
        s = start_server()
        dict_auth = {
            'action': 'authenticate',
            'time': datetime.datetime.now(),
            'user': {
                'user_name': login,
                'password': password
            }
        }
        secret_message = os.urandom(32)
        dict_auth['secret_message'] = secret_message
        hash = hmac.new(secret_key, secret_message, hashlib.sha256)
        digest = hash.digest()
        s.send(pickle.dumps(dict_auth))
        auth_data = s.recv(1024)
        auth_data_loads = pickle.loads(auth_data)
        if hmac.compare_digest(digest, auth_data_loads['digest']) and auth_data_loads['response'] == 200:
            self.client_obj = client.ClientPage(s)
            self.client_obj.show()
            self.client_obj.start_client(login)



if __name__ == '__main__':
    try:
        s = start_server()
        app = QtWidgets.QApplication(sys.argv)
        auth = AuthPage()
        auth.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(e)
