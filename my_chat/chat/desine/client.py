from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal, pyqtSlot

import importlib.util
import importlib

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


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

print(session.query(my_server.Clients).all())
