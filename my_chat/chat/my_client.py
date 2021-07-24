from socket import socket, AF_INET, SOCK_STREAM
import dis
import time
import pickle
import logging
from functools import wraps
import datetime
from threading import Thread
import inspect
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, Text, Time

logger = logging.getLogger('my_client')

users = {
    'KonTroAll': 'SpaceShip007',
    'test': 'test',
    'test2': 'test2',
    'test3': 'test3',
    'Julia': 'SpaceShuttle007'
}

usernames_auth = []
room_names = ['#smalltalk']
users_contacts = ['KonTroAll', 'test2', 'Julia', 'test']

dict_signals = {
    100: 'welcome!',
    101: 'do not come here!',
    102: 'logout',
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

test = True
timestamp = datetime.datetime.now()


# декоратор
def client_log_dec(func):
    @wraps(func)
    def call(*args, **kwargs):
        res = func(*args, **kwargs)
        logger.info(f'{datetime.datetime.now()} Call {func.__name__}: {args}, {kwargs}')
        return res

    return call


def find_forbidden_methods_call(func, method_names):
    for instr in dis.get_instructions(func):
        if instr.opname == 'LOAD_METHOD' and instr.argval in method_names:
            return instr.argval


# метакласс ClientVerifier
class ClientVerifierMeta(type):
    forbidden_method_names = ('accept', 'listen', 'SOCK_DGRAM')

    def __init__(self, name, bases, class_dict):
        for key, val in class_dict.items():
            if inspect.isfunction(val):
                method_name = find_forbidden_methods_call(val, self.forbidden_method_names)
                if method_name:
                    raise ValueError(f'called forbidden method "{method_name}"')
            elif isinstance(val, socket):
                raise ValueError('Socket object cannot be defined in class definition')

        super(ClientVerifierMeta, self).__init__(name, bases, class_dict)


class Client(metaclass=ClientVerifierMeta):
    def __init__(self):
        self.s = None

    def create_socket(self):
        self.s = socket(AF_INET, SOCK_STREAM)
        return self.s

    def start_connection(self, host, port, s):
        self.s = s
        s.connect((host, port))

    def user_auth(self, username, password):
        dict_auth = {
            'action': 'authenticate',
            'time': timestamp,
            'user': {
                'user_name': username,
                'password': password
            }
        }
        self.s.send(pickle.dumps(dict_auth))
        auth_data = self.s.recv(1024)
        auth_data_loads = pickle.loads(auth_data)
        if auth_data_loads['response'] == 200:
            usernames_auth.append(username)
        logger.info(auth_data_loads)
        print('Сообщение от сервера: ', pickle.loads(auth_data), ', длиной ', len(auth_data), ' байт')

        return auth_data_loads

    def user_presence(self):
        logger.info('start user_presence!')
        pre_data = self.s.recv(1024)
        pre_data_load = pickle.loads(pre_data)
        if pre_data_load['action'] == 'probe':
            presence_dict = {
                'action': 'presence',
                'time': timestamp,
                'type': 'status',
                'user': {
                    'username': usernames_auth[0],
                    'status': 'I am still here!'
                }
            }
            self.s.send(pickle.dumps(presence_dict))
            return presence_dict
        else:
            return 'error!'

    def message_send_user(self, message, to):
        logger.info('start message_to_user!')
        message_dict = {
            'action': 'msg',
            'time': timestamp,
            'to': to,
            'from': usernames_auth[0],
            'encoding': 'utf-8',
            'message': message
        }

        self.s.send(pickle.dumps(message_dict))

    def get_contacts(self, username):
        contacts_dict = {
            "action": "get_contacts",
            "time": str(timestamp),
            "user_name": username
        }
        self.s.send(pickle.dumps(contacts_dict))

    def add_contacts(self, username, new_contact):
        new_contact_dict = {
            'action': 'add_contact',
            'new_contact': new_contact,
            'time': str(timestamp),
            'user_name': username
        }
        self.s.send(pickle.dumps(new_contact_dict))

    def logout(self):
        logout_dict = {
            'action': 'logout',
            'time': timestamp,
            'from': usernames_auth[0]
        }
        self.s.send(pickle.dumps(logout_dict))
        return logout_dict


# Авторизация пользователя на сервере
# @client_log_dec
# def user_authenticate(s, username, password):
#     logger.info('start user_authenticate!')
#     dict_auth = {
#         'action': 'authenticate',
#         'time': timestamp,
#         'user': {
#             'user_name': username,
#             'password': password
#         }
#     }
#     s.send(pickle.dumps(dict_auth))
#     auth_data = s.recv(1024)
#     auth_data_loads = pickle.loads(auth_data)
#     if auth_data_loads['response'] == 200:
#         usernames_auth.append(username)
#     logger.info(auth_data_loads)
#     print('Сообщение от сервера: ', pickle.loads(auth_data), ', длиной ', len(auth_data), ' байт')
#
#     return auth_data_loads
#
#
# # Проверка присутствия пользователя
# @client_log_dec
# def user_presence(s):
#     logger.info('start user_presence!')
#     pre_data = s.recv(1024)
#     pre_data_load = pickle.loads(pre_data)
#     if pre_data_load['action'] == 'probe':
#         presence_dict = {
#             'action': 'presence',
#             'time': timestamp,
#             'type': 'status',
#             'user': {
#                 'username': usernames_auth[0],
#                 'status': 'I am still here!'
#             }
#         }
#         s.send(pickle.dumps(presence_dict))
#         return presence_dict
#     else:
#         return 'error!'
#
#
# # Отправка сообщения другому пользователю
# @client_log_dec
# def message_send_user(s, to, message):
#     logger.info('start message_to_user!')
#     message_dict = {
#         'action': 'msg',
#         'time': str(timestamp),
#         'to': to,
#         'from': usernames_auth[0],
#         'encoding': 'utf-8',
#         'message': message
#     }
#     s.send(pickle.dumps(message_dict))
#
#
# @client_log_dec
# def message_send_room(s, to, message):
#     logger.info('start message_to_user!')
#     message_dict = {
#         'action': 'msg',
#         'time': timestamp,
#         'to': to,
#         'from': usernames_auth[0],
#         'encoding': 'utf-8',
#         'message': message,
#     }
#     s.send(pickle.dumps(message_dict))


def message_recv(s):
    while True:
        message_data = s.recv(1024)
        message_data_load = pickle.loads(message_data)
        if message_data_load['message'] == 'Q':
            break
        elif message_data_load['message'] == 'get_contacts':
            print(f"Ваш список контактов: {message_data_load['alert']}")
        elif message_data_load['message'] == 'add_contact':
            print('Сообщение от сервера: ', message_data_load, ', длиной ', len(message_data), ' байт')
        elif message_data_load['message'] == 'add_group':
            print('Сообщение от сервера: ', message_data_load, ', длиной ', len(message_data), ' байт')
        else:
            print(f'{message_data_load["to"]} from {message_data_load["from"]}: {message_data_load["message"]}')
        logger.info(message_data_load)


def logout(s):
    logout_dict = {
        'action': 'logout',
        'time': timestamp,
        'from': usernames_auth[0]
    }
    s.send(pickle.dumps(logout_dict))
    return logout_dict


def main():
    HOST = 'localhost'
    PORT = 7777

    logger.info('start connection!')

    client = Client()
    s = client.create_socket()
    client.start_connection(HOST, PORT, s)

    while True:
        start = input('Добро пожаловать! Хотите авторизоваться? (Y / N): ')
        if start.upper() == 'Y':
            username = input('Enter your login: ')
            password = input('Enter your password: ')
            if username in usernames_auth:
                auth_dict = {
                    'time': timestamp,
                    'response': 409,
                    'message': dict_signals[409]
                }
                print(auth_dict)
            # client.user_auth(username, password)
            if client.user_auth(username, password)['response'] == 402:
                break

            client.user_presence()

            msg = Thread(target=message_recv, args=(s,))
            msg.start()
            while True:
                user_choice = input(
                    "Введите, что вы хотите сделать (К/Показать список контактов, ДК/Добавить новый контакт, П/Отправить сообщение пользователю, Г/Отправить группе, ВГ/Вступить в группу). Чтобы выйти введите: 'Q': ")

                if user_choice.upper() == 'ВГ':
                    to = input('Введите имя группы (Ввод должен начинаться с #, Пример:#5556): ')
                    if to not in room_names:
                        a = input("Группа найдена не была, хотите создать группу с таким именем? (Y / N): ")
                        if a.upper() == 'Y':
                            room_names.append(to)
                            s.send(pickle.dumps({'action': 'add_group', 'room_name': to}))
                            msg.join(timeout=1)
                elif user_choice.upper() == 'П':
                    to = input('Кому отправить сообщение: ')
                    message = input('Enter message: ')
                    client.message_send_user(message, to)
                    msg.join(timeout=1)
                elif user_choice.upper() == 'Г':
                    to = input('Кому отправить сообщение: ')
                    message = input('Enter message: ')
                    client.message_send_user(message, to)
                    msg.join(timeout=1)
                elif user_choice.upper() == 'К':
                    client.get_contacts(username)
                    msg.join(timeout=1)
                elif user_choice.upper() == 'ДК':
                    new_contact = input('Введите имя контакта: ')
                    if new_contact in users.keys():
                        users_contacts.append(new_contact)
                    else:
                        print('Пользователь не найден!')
                    client.add_contacts(username, new_contact)
                    msg.join(timeout=1)
                elif user_choice.upper() == 'Q':
                    message_dict = {
                        'action': 'msg',
                        'message': user_choice.upper()
                    }
                    s.send(pickle.dumps(message_dict))
                    break

            msg.join(timeout=1)

            client.logout()
            quit_data = s.recv(1024)
            logger.info(pickle.loads(quit_data))
            usernames_auth.clear()
            print('Сообщение от сервера: ', pickle.loads(quit_data), ', длиной ', len(quit_data), ' байт \n')
        else:
            print('До свидания!')
            break
    s.close()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
