import unittest
from big_task.my_client import user_authenticate, message_to_user, message_to_all, user_presence
import time



class TestClient(unittest.TestCase):

    # для прохождения всех тестов поменять assertNotEqual на assertEqual

    def test_user_auth(self):
        self.assertNotEqual(user_authenticate('KonTroAll', 'SpaceShip007')['user']['user_name'], 'KonTroAll')

    def test_user_presence(self):
        dict_probe = {
            'action': 'probe',
            'time': int(time.time())
        }
        self.assertNotEqual(user_presence(dict_probe)['action'], 'presence')

    def test_user_to_user_message(self):
        self.assertNotEqual(message_to_user('KonTroAll', 'Julia', 'Hello world!')['to'], 'Julia')

    def test_user_to_all_message(self):
        self.assertNotEqual(message_to_all('KonTroAll', '#smalltalk', 'Hello world!')['to'], '#smalltalk')


if __name__ == "__main__":
    unittest.main()