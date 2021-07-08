from socket import socket, AF_INET, SOCK_STREAM
import time
import pickle
import logging
from functools import wraps
import datetime
from threading import Thread

logger = logging.getLogger('my_client')

users = {
    'KonTroAll': 'SpaceShip007',
    'test': 'test',
    'test2': 'test2',
    'Julia': 'SpaceShuttle007'
}

usernames_auth = []
room_names = ['#smalltalk']

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
timestamp = int(time.time())


# декоратор
def client_log_dec(func):
    @wraps(func)
    def call(*args, **kwargs):
        res = func(*args, **kwargs)
        logger.info(f'{datetime.datetime.now()} Call {func.__name__}: {args}, {kwargs}')
        return res

    return call


# Авторизация пользователя на сервере
@client_log_dec
def user_authenticate(s, username, password):
    logger.info('start user_authenticate!')
    dict_auth = {
        'action': 'authenticate',
        'time': timestamp,
        'user': {
            'user_name': username,
            'password': password
        }
    }
    s.send(pickle.dumps(dict_auth))
    auth_data = s.recv(1024)
    auth_data_loads = pickle.loads(auth_data)
    if auth_data_loads['response'] == 200:
        usernames_auth.append(username)
    logger.info(auth_data_loads)
    print('Сообщение от сервера: ', pickle.loads(auth_data), ', длиной ', len(auth_data), ' байт')

    return auth_data_loads


# Проверка присутствия пользователя
@client_log_dec
def user_presence(s):
    logger.info('start user_presence!')
    pre_data = s.recv(1024)
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
        s.send(pickle.dumps(presence_dict))
        return presence_dict
    else:
        return 'error!'


# Отправка сообщения другому пользователю
@client_log_dec
def message_send_user(s, to, message):
    logger.info('start message_to_user!')
    message_dict = {
        'action': 'msg',
        'time': timestamp,
        'to': to,
        'from': usernames_auth[0],
        'encoding': 'utf-8',
        'message': message
    }
    s.send(pickle.dumps(message_dict))


@client_log_dec
def message_send_room(s, to, message):
    logger.info('start message_to_user!')
    message_dict = {
        'action': 'msg',
        'time': timestamp,
        'to': to,
        'from': usernames_auth[0],
        'encoding': 'utf-8',
        'message': message,
    }
    s.send(pickle.dumps(message_dict))


def message_recv(s):
    while True:
        message_data = s.recv(1024)
        message_data_load = pickle.loads(message_data)
        if message_data_load['message'] == 'Q':
            break
        elif message_data_load['message'] == 'add_group':
            print('Сообщение от сервера: ', message_data_load, ', длиной ', len(message_data), ' байт')
        else:
            if message_data_load['to'][0].isalpha():
                print('Сообщение от сервера: ', message_data_load, ', длиной ', len(message_data), ' байт')
            else:
                print(
                    f'{message_data_load["to"]} from {message_data_load["from"]}: {message_data_load["message"]}')
        logger.info(message_data_load)


def logout(s):
    logout_dict = {
        'action': 'logout',
        'time': timestamp,
        'from': usernames_auth[0]
    }
    s.send(pickle.dumps(logout_dict))
    return logout_dict


def main(s):
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
            else:
                if user_authenticate(s, username, password)['response'] == 402:
                    break

            user_presence(s)


            while True:
                msg = Thread(target=message_recv, args=(s,))
                msg.start()
                user_choice = input(
                    "Введите, что вы хотите сделать (П/Отправить сообщение пользователю, Г/Отправить группе, ВГ/Вступить в группу). Чтобы выйти введите: 'Q': ")

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
                    message_send_user(s, to, message)
                    msg.join(timeout=1)
                elif user_choice.upper() == 'Г':
                    to = input('Кому отправить сообщение: ')
                    message = input('Enter message: ')
                    message_send_room(s, to, message)
                    msg.join(timeout=1)
                elif user_choice.upper() == 'Q':
                    message_dict = {
                        'action': 'msg',
                        'message': user_choice.upper()
                    }
                    s.send(pickle.dumps(message_dict))
                    msg.join(timeout=1)
                    break

            logout(s)
            quit_data = s.recv(1024)
            logger.info(pickle.loads(quit_data))
            usernames_auth.clear()
            print('Сообщение от сервера: ', pickle.loads(quit_data), ', длиной ', len(quit_data), ' байт \n')
        else:
            print('До свидания!')
            break


if __name__ == '__main__':
    try:
        s = socket(AF_INET, SOCK_STREAM)
        s.connect(('localhost', 8007))
        logger.info('start connection!')
        main(s)
        s.close()
    except Exception as e:
        print(e)
