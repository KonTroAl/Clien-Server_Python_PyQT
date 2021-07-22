from socket import socket, AF_INET, SOCK_STREAM
import dis
import time
import pickle
import logging
from functools import wraps
import datetime
import select
import inspect

from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, Text, Time

logger = logging.getLogger('my_server')

timestamp = int(time.time())

users = {
    'KonTroAll': 'SpaceShip007',
    'test': 'test',
    'test2': 'test2',
    'test3': 'test3',
    'Julia': 'SpaceShuttle007'
}

users_contacts = ['KonTroAll', 'test2', 'Julia', 'test']
usernames_auth = []
room_names = ['#smalltalk']

dict_signals = {
    100: 'welcome!',
    101: 'do not come here!',
    200: 'OOK!',
    201: 'created',
    202: 'accepted',
    400: 'неправильный запрос/JSON-объект',
    401: 'не авторизован',
    402: 'неправильный логин/пароль',
    403: 'пользователь заблокирован',
    404: 'пользователь/чат отсутствует на сервере',
    409: 'уже имеется подключение с указанным логином',
    410: 'адресат существует, но недоступен (offline)',
    500: 'ошибка сервера'
}


def server_log_dec(func):
    @wraps(func)
    def call(*args, **kwargs):
        res = func(*args, **kwargs)
        logger.info(f'{datetime.datetime.now()} Call {func.__name__}: {args}, {kwargs}')
        return res

    return call


# Авторизация пользователя на сервере
@server_log_dec
def user_authenticate(my_dict, sock):
    logger.info('start user_authenticate!')
    dict_auth_response = {}
    user = my_dict['user']
    for us in users.keys():
        if us == user['user_name']:
            usernames_auth.append(us)

    if user['user_name'] in usernames_auth and users[user['user_name']] == user['password']:
        dict_auth_response['response'] = 200
        dict_auth_response['alert'] = dict_signals[dict_auth_response['response']]
        print('authenticate completed!')
        logger.info('authenticate completed!')
        sock.send(pickle.dumps(dict_auth_response))
        return dict_auth_response
    else:
        dict_auth_response['response'] = 402
        dict_auth_response['alert'] = dict_signals[dict_auth_response['response']]
        print('error!')
        logger.info('error!')
        sock.send(pickle.dumps(dict_auth_response))
        return dict_auth_response


# Проверка присутствия пользователя
@server_log_dec
def presence_user(client, sock):
    dict_probe = {
        'action': 'probe',
        'time': timestamp
    }

    sock.send(pickle.dumps(dict_probe))

    pre_data = client.recv(1024)
    pre_data_load = pickle.loads(pre_data)
    print('Сообщение от клиента: ', pre_data_load, ', длиной ', len(pre_data), ' байт')
    return pre_data_load['action']


# Отправка сообщения другому пользователю
@server_log_dec
def message_send(my_dict, sock):
    msg_dict = {
        'time': timestamp
    }
    if list(my_dict['to'])[0].isalpha():
        for i in users_contacts:
            if my_dict['to'] == i:
                msg_dict['response'] = 200
                msg_dict['alert'] = dict_signals[msg_dict['response']]
                msg_dict['message'] = my_dict['message']
                msg_dict['to'] = my_dict['to']
                msg_dict['from'] = my_dict['from']
                print('message send!')
                logger.info('message send!')
                sock.send(pickle.dumps(msg_dict))
                return msg_dict
            else:
                msg_dict['response'] = 404
                msg_dict['alert'] = dict_signals[msg_dict['response']]
                msg_dict['message'] = my_dict['message']
                msg_dict['to'] = my_dict['to']
                msg_dict['from'] = my_dict['from']
                logger.info('пользователь/чат отсутствует на сервере')
                sock.send(pickle.dumps(msg_dict))
                return msg_dict


def message_room(my_dict, sock):
    msg_dict = {
        'time': timestamp
    }
    if my_dict['to'] in room_names:
        msg_dict['response'] = 200
        msg_dict['to'] = my_dict['to']
        msg_dict['from'] = my_dict['from']
        msg_dict['message'] = my_dict['message']
        return msg_dict
    else:
        msg_dict['response'] = 404
        logger.info('пользователь/чат отсутствует на сервере')
        sock.send(pickle.dumps(msg_dict))
        return msg_dict


def message_room_send(my_dict, w):
    for val in w:
        val.send(pickle.dumps(my_dict))
    print('message send!')
    logger.info('message send!')


def read_requests(r_clients, all_clients):
    """ Чтение запросов из списка клиентов
    """
    responses = {}  # Словарь ответов сервера вида {сокет: запрос}

    for sock in r_clients:
        try:
            data = pickle.loads(sock.recv(1024))
            responses[sock] = data
        except:
            print('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
            all_clients.remove(sock)

    return responses


engine = create_engine('sqlite:///sqlite3.db', echo=True, pool_recycle=7200)
Session = sessionmaker(bind=engine)
Session.configure(bind=engine)

Base = declarative_base()
metadata = Base.metadata


class Clients(Base):
    __tablename__ = 'clients'
    id = Column(Integer, primary_key=True)
    user_name = Column(String)
    password = Column(String)
    info = Column(Text)

    def __init__(self, user_name, password, info):
        self.user_name = user_name
        self.password = password
        self.info = info

    def __repr__(self):
        return "<Client('%s', '%s')>" % (self.user_name, self.info)


class ClientHistory(Base):
    __tablename__ = 'client_history'
    login_time = Column(Time)
    ip_address = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('clients.id'), nullable=False)

    def __init__(self, login_time, ip_address, user_id):
        self.login_time = login_time
        self.ip_address = ip_address
        self.user_id = user_id

    def __repr__(self):
        return "<ClientHistory('%s', '%s', '%s')>" % (self.login_time, self.ip_address, self.user_id)


class ClientContacts(Base):
    __tablename__ = 'client_contacts'
    id_owner = Column(Integer, ForeignKey('clients.id'), primary_key=True)
    id_client = Column(Integer, ForeignKey('clients.id'))

    def __init__(self, id_owner, id_client):
        self.id_owner = id_owner
        self.id_client = id_client

    def __repr__(self):
        return "<ClientContacts('%s', '%s')>" % (self.id_owner, self.id_client)


metadata.create_all(engine)

session = Session()

admin_user = Clients('test', 'test', 'admin')
session.add(admin_user)
session.commit()
q_user = session.query(Clients).filter_by(user_name='test').first()
print(q_user)


def find_forbidden_methods_call(func, method_names):
    for instr in dis.get_instructions(func):
        if instr.opname == 'LOAD_METHOD' and instr.argval in method_names:
            return instr.argval


class ServerVerifierMeta(type):

    def __init__(self, *args, **kwargs):
        forbidden_method_names = ('connect', 'SOCK_DGRAM')

        def __init__(self, name, bases, class_dict):
            for key, val in class_dict.items():
                if inspect.isfunction(val):
                    method_name = find_forbidden_methods_call(val, self.forbidden_method_names)
                    if method_name:
                        raise ValueError(f'called forbidden method "{method_name}"')

            super(ServerVerifierMeta, self).__init__(name, bases, class_dict)


class PortVerifier:

    def __init__(self, port=7777):
        self.port = port

    def __get__(self, instance, owner):
        return self.port

    def __set__(self, instance, value):
        print('start port verification!')
        if value != 7777:
            raise ValueError("Wrong port number!")
        print('verification complete!')


class Server(metaclass=ServerVerifierMeta):
    port = PortVerifier()

    def __init__(self):
        self.s = None

    def create_socket(self):
        self.s = socket(AF_INET, SOCK_STREAM)
        return self.s

    def start_server(self):
        self.client, self.addr = self.s.accept()

    def client_return(self):
        return self.client

    def addr_return(self):
        return self.addr

    def user_authenticate(self, my_dict, sock):
        # self.s = socket(AF_INET, SOCK_STREAM)
        logger.info('start user_authenticate!')
        # self.s.send(pickle.dumps('start!'))
        dict_auth_response = {}
        user = my_dict['user']
        for us in users.keys():
            if us == user['user_name']:
                usernames_auth.append(us)

        if user['user_name'] in usernames_auth and users[user['user_name']] == user['password']:
            dict_auth_response['response'] = 200
            dict_auth_response['alert'] = dict_signals[dict_auth_response['response']]
            print('authenticate completed!')
            logger.info('authenticate completed!')
            sock.send(pickle.dumps(dict_auth_response))
            return dict_auth_response
        else:
            dict_auth_response['response'] = 402
            dict_auth_response['alert'] = dict_signals[dict_auth_response['response']]
            print('error!')
            logger.info('error!')
            sock.send(pickle.dumps(dict_auth_response))
            return dict_auth_response

    def presence_user(self, client, sock):
        dict_probe = {
            'action': 'probe',
            'time': timestamp
        }

        sock.send(pickle.dumps(dict_probe))

        pre_data = client.recv(1024)
        pre_data_load = pickle.loads(pre_data)
        print('Сообщение от клиента: ', pre_data_load, ', длиной ', len(pre_data), ' байт')
        return pre_data_load['action']

    def message_send(self, my_dict, sock):
        msg_dict = {
            'time': timestamp
        }
        if list(my_dict['to'])[0].isalpha():
            for i in users_contacts:
                if my_dict['to'] == i:
                    msg_dict['response'] = 200
                    msg_dict['alert'] = dict_signals[msg_dict['response']]
                    msg_dict['message'] = my_dict['message']
                    msg_dict['to'] = my_dict['to']
                    msg_dict['from'] = my_dict['from']
                    print('message send!')
                    logger.info('message send!')
                    sock.send(pickle.dumps(msg_dict))
                    return msg_dict
                else:
                    msg_dict['response'] = 404
                    msg_dict['alert'] = dict_signals[msg_dict['response']]
                    msg_dict['message'] = my_dict['message']
                    msg_dict['to'] = my_dict['to']
                    msg_dict['from'] = my_dict['from']
                    logger.info('пользователь/чат отсутствует на сервере')
                    sock.send(pickle.dumps(msg_dict))
                    return msg_dict

    def message_room(self, my_dict, sock):
        msg_dict = {
            'time': timestamp
        }
        if my_dict['to'] in room_names:
            msg_dict['response'] = 200
            msg_dict['to'] = my_dict['to']
            msg_dict['from'] = my_dict['from']
            msg_dict['message'] = my_dict['message']
            return msg_dict
        else:
            msg_dict['response'] = 404
            logger.info('пользователь/чат отсутствует на сервере')
            sock.send(pickle.dumps(msg_dict))
            return msg_dict

    def message_room_send(self, my_dict, w):
        for val in w:
            val.send(pickle.dumps(my_dict))
        print('message send!')
        logger.info('message send!')

    def get_contacts(self, my_dict, sock):
        contacts_dict = {
            'response': 200,
            'alert': users_contacts,
            'message': 'get_contacts'
        }
        sock.send(pickle.dumps(contacts_dict))

    def add_contacts(self, my_dict, sock):
        users_contacts.append(my_dict['new_contact'])
        contacts_dict = {
            'response': 200,
            'alert': dict_signals[200],
            'message': 'add_contact'
        }
        sock.send(pickle.dumps(contacts_dict))

    def read_requests(self, r_clients, all_clients):
        """ Чтение запросов из списка клиентов
        """
        responses = {}  # Словарь ответов сервера вида {сокет: запрос}

        for sock in r_clients:
            try:
                data = pickle.loads(sock.recv(1024))
                responses[sock] = data
            except:
                print('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
                all_clients.remove(sock)

        return responses


def main():
    server = Server()
    s = server.create_socket()
    num_port = 7777
    s.bind(('', int(num_port)))
    s.listen(5)
    s.settimeout(0.2)
    server.port = num_port

    logger.info('start connection!')
    clients = []

    while True:
        try:
            # client, addr = s.accept()
            server.start_server()
        except OSError as e:
            pass
        else:
            print("Получен запрос на соединение от %s" % str(server.addr_return()))
            clients.append(server.client_return())

        finally:
            r = []
            w = []
            try:
                r, w, e = select.select(clients, clients, [])
            except:
                pass

            requests = read_requests(r, clients)
            if requests:
                for sock in w:
                    if sock in requests:
                        if requests[sock]['action'] == 'authenticate':
                            auth = server.user_authenticate(requests[sock], sock)['response']
                            if auth == 402:
                                usernames_auth.remove(requests[sock]['user']['user_name'])
                                break
                            server.presence_user(sock, sock)
                        elif requests[sock]['action'] == 'msg':
                            if requests[sock]['message'].upper() == 'Q':
                                sock.send(pickle.dumps(requests[sock]))
                            else:
                                if requests[sock]['to'][0].isalpha():
                                    server.message_send(requests[sock], sock)
                                else:
                                    server.message_room_send(server.message_room(requests[sock], sock), w)
                        elif requests[sock]['action'] == 'logout':
                            usernames_auth.remove(requests[sock]['from'])
                            sock.send(pickle.dumps({'action': 'quit'}))
                        elif requests[sock]['action'] == 'get_contacts':
                            server.get_contacts(requests[sock], sock)
                        elif requests[sock]['action'] == 'add_contact':
                            server.add_contacts(requests[sock], sock)
                        elif requests[sock]['action'] == 'add_group':
                            room_names.append(requests[sock]['room_name'])
                            sock.send(
                                pickle.dumps({'response': 200, 'alert': dict_signals[200], 'message': 'add_group'}))


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
