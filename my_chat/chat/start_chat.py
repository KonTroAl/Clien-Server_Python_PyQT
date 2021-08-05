# Продолжаем работать над проектом «Мессенджер»:
# Реализовать скрипт, запускающий два клиентских приложения: на чтение чата
# и на запись в него.
# Уместно использовать модуль subprocess);
# Реализовать скрипт, запускающий указанное количество клиентских приложений.

import subprocess


def start_chat(n):
    subprocess.Popen('C:\programming\PyQT\HW\my_chat\chat\my_server.py', shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
    while n > 0:
        subprocess.Popen('C:\programming\PyQT\HW\my_chat\chat\my_client.py', shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)


if __name__ == '__main__':
    n = 2
    start_chat(n)
