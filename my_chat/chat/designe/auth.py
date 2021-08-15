import sys
import os
import hashlib
import hmac
import datetime
import pickle

from PyQt5 import QtWidgets

import importlib.util
import importlib

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from auth_page import Ui_MainWindow
import admin
import client


def module_from_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


admin_dict = {
    'login': 'admin',
    'password': 'admin'
}

secret_key = b'test_test'
my_server = module_from_file('my_server', '../my_server.py')
my_client = module_from_file('my_client', '../my_client.py')

engine = create_engine('sqlite:///../sqlite3.db', echo=True, pool_recycle=7200)
Session = sessionmaker(bind=engine)
Session.configure(bind=engine)

session = Session()


class AuthPage(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.SubmitButton.clicked.connect(self.auth)

    def start_server(self):
        HOST = 'localhost'
        PORT = 7777
        client = my_client.Client()
        s = client.create_socket()
        client.start_connection(HOST, PORT, s)
        return s

    def auth(self):
        login = self.ui.LoginBox.text()
        password = self.ui.PasswordBox.text()

        s = self.start_server()
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
            self.ui.MainHedding.setText('Авторизация завершена! Добро Пожаловать!')



if __name__ == '__main__':
    try:
        app = QtWidgets.QApplication(sys.argv)
        auth = AuthPage()
        admin = admin.AdminDialog()
        client = client.ClientPage()

        auth.show()
        admin.show()

        sys.exit(app.exec_())
    except Exception as e:
        print(e)
