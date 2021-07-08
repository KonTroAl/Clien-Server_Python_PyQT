# 2. В каждом модуле выполнить настройку соответствующего логгера по следующему алгоритму:
#   a. Создание именованного логгера;
#   b. Сообщения лога должны иметь следующий формат: "<дата-время> <уровень_важности> <имя_модуля> <сообщение>";
#   c. Журналирование должно производиться в лог-файл;
#   d. На стороне сервера необходимо настроить ежедневную ротацию лог-файлов.
# 3. Реализовать применение созданных логгеров для решения двух задач:
#   a. Журналирование обработки исключений try/except. Вместо функции print() использовать журналирование и обеспечить вывод служебных сообщений в лог-файл;
#   b. Журналирование функций, исполняемых на серверной и клиентской сторонах при работе мессенджера.

import logging

logging.basicConfig(
    filename='logs/client.log',
    format = "%(asctime)s %(levelname)s %(module)-10s %(message)s",
    level= logging.DEBUG
)

logger = logging.getLogger('logs/my_client')

# Создание обработчиков
format = logging.Formatter("%(asctime)s %(levelname)s %(module)-10s %(message)s")
client_hand = logging.FileHandler('logs/my_client.log', encoding='utf-8')
client_hand.setLevel(logging.INFO)
client_hand.setFormatter(format)

logger.addHandler(client_hand)

if __name__ == '__main__':
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    logger.addHandler(console)
    logger.info('Тестовый запуск логирования')