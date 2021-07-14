from socket import socket, AF_INET, SOCK_STREAM
import dis
import time
import pickle
import logging
from functools import wraps
import datetime
import select

logger = logging.getLogger('my_server')

timestamp = int(time.time())

users = {
    'KonTroAll': 'SpaceShip007',
    'test': 'test',
    'test2': 'test2',
    'Julia': 'SpaceShuttle007'
}

usernames_friends = ['Julia', 'test']
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
        for i in usernames_friends:
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


class ServerVerifierMeta(type):

    def __init__(self, *args, **kwargs):
        for key, val in self.__dict__.items():
            if key == 'start_server':
                bytecode = dis.Bytecode(self.__dict__[key])
                for i in bytecode:
                    if i.opname == 'LOAD_METHOD':
                        if i.argval == 'listen' or 'accept':
                            continue
                        else:
                            print('error!')
            elif key == 'create_socket':
                bytecode = dis.Bytecode(self.__dict__[key])
                for i in bytecode:
                    if i.opname == 'LOAD_METHOD':
                        if i.argval == 'AF_INET' or 'SOCK_STREAM':
                            continue
                        else:
                            print('error!')
        super(ServerVerifierMeta, self).__init__(*args, **kwargs)


class ServerVerifier(metaclass=ServerVerifierMeta):
    pass


class PortVerifier:

    def __init__(self, port):
        self.port = port

    def __set__(self, instance, value):
        print('start port verification!')
        if value != 7777:
            raise ValueError("Wrong port number!")
        print('verification complete!')


class Server(ServerVerifier):
    port = PortVerifier('port')

    def __init__(self):
        self.s = None

    def create_socket(self):
        self.s = socket(AF_INET, SOCK_STREAM)
        return self.s

    def start_server(self):

        clients = []
        while True:
            try:
                client, addr = self.s.accept()
            except OSError as e:
                pass
            else:
                print("Получен запрос на соединение от %s" % str(addr))
                clients.append(client)

            finally:
                r = []
                w = []
                try:
                    r, w, e = select.select(clients, clients, [])
                except:
                    pass

                requests = read_requests(r, clients)


def main():
    s = socket(AF_INET, SOCK_STREAM)
    s.bind(('', 8007))
    s.listen(5)
    s.settimeout(0.2)
    logger.info('start connection!')
    clients = []

    while True:
        try:
            client, addr = s.accept()
        except OSError as e:
            pass
        else:
            print("Получен запрос на соединение от %s" % str(addr))
            clients.append(client)

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
                            if user_authenticate(requests[sock], sock)['response'] == 402:
                                usernames_auth.remove(requests[sock]['user']['user_name'])
                                break
                            presence_user(sock, sock)
                        elif requests[sock]['action'] == 'msg':
                            if requests[sock]['message'].upper() == 'Q':
                                sock.send(pickle.dumps(requests[sock]))
                            else:
                                if requests[sock]['to'][0].isalpha():
                                    message_send(requests[sock], sock)
                                else:
                                    message_room_send(message_room(requests[sock], sock), w)
                        elif requests[sock]['action'] == 'logout':
                            usernames_auth.remove(requests[sock]['from'])
                            sock.send(pickle.dumps({'action': 'quit'}))
                        elif requests[sock]['action'] == 'add_group':
                            room_names.append(requests[sock]['room_name'])
                            sock.send(
                                pickle.dumps({'response': 200, 'alert': dict_signals[200], 'message': 'add_group'}))


if __name__ == '__main__':
    try:
        # s = socket(AF_INET, SOCK_STREAM)

        # main()
        server = Server()
        s = server.create_socket()
        num_port = 7777
        s.bind(('', int(num_port)))
        s.listen(5)
        s.settimeout(0.2)
        server.port = num_port

        server.start_server()
    except Exception as e:
        print(e)
