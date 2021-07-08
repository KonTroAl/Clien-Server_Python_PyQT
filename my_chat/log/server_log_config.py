import logging
from logging import handlers

logging.basicConfig(
    filename='logs/server.log',
    format = "%(asctime)s %(levelname)s %(module)-10s %(message)s",
    level= logging.DEBUG
)

logger = logging.getLogger('my_server')

# Создание обработчиков
format = logging.Formatter("%(asctime)s %(levelname)s %(module)-10s %(message)s")
# server_hand = logging.FileHandler('logs/my_server.log', encoding='utf-8')
#
# server_hand.setLevel(logging.INFO)
# server_hand.setFormatter(format)
server_time_hand = logging.handlers.TimedRotatingFileHandler('logs/my_server.log', when='midnight', interval=1)
server_time_hand.setLevel(logging.INFO)
server_time_hand.setFormatter(format)

# logger.addHandler(server_hand)
logger.addHandler(server_time_hand)



if __name__ == '__main__':
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    logger.addHandler(console)
    logger.info('Тестовый запуск логирования')
