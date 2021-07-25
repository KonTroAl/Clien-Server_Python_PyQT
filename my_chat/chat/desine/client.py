from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal, pyqtSlot

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import importlib.util, importlib

spec = importlib.util.spec_from_file_location('my_server', '../my_server.py')
module = importlib.util.module_from_spec(spec)
my_server = spec.loader.exec_module(module)

#
# # session = my_server.session
#
# print(session.query(my_server.Clients).filter_by(user_name='test').one())
