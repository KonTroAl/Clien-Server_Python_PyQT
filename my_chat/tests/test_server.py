import unittest
import time
from big_task.my_server import user_authenticate, presence_user, message_to_user, message_to_room

timestamp = int(time.time())


class TestClient(unittest.TestCase):

    # для прохождения всех тестов поменять assertNotEqual на assertEqual

    def test_user_authenticate(self):
        dict_auth_test = {
            'action': 'authenticate',
            'time': timestamp,
            'user': {
                'user_name': 'KonTroAll',
                'password': 'SpaceShip007'
            }
        }
        self.assertNotEqual(user_authenticate(dict_auth_test)['response'], 200)

    def test_user_presence(self):
        presence_dict = {
            'action': 'presence',
            'time': timestamp,
            'type': 'status',
            'user': {
                'username': 'KonTroAll',
                'status': 'I am still here!'
            }
        }
        self.assertNotEqual(presence_user(presence_dict), 'presence')

    def test_message_to_user(self):
        message_dict = {
            'action': 'msg',
            'time': timestamp,
            'to': 'Julia',
            'from': 'KonTroAll',
            'encoding': 'utf-8',
            'message': 'Hello world!'
        }
        self.assertNotEqual(message_to_user(message_dict)['response'], 200)

    def test_message_to_all(self):
        message_dict = {
            'action': 'msg',
            'time': timestamp,
            'to': '#smalltalk',
            'from': 'KonTroAll',
            'encoding': 'utf-8',
            'message': 'Hello world!'
        }
        self.assertNotEqual(message_to_room(message_dict)['response'], 200)


if __name__ == "__main__":
    unittest.main()