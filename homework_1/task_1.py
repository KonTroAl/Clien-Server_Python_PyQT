# task 1
# Написать функцию host_ping(), в которой с помощью утилиты ping будет проверяться доступность сетевых узлов.
# Аргументом функции является список, в котором каждый сетевой узел должен быть представлен именем хоста или ip-адресом.
# В функции необходимо перебирать ip-адреса и проверять их доступность с выводом соответствующего сообщения
# («Узел доступен», «Узел недоступен»). При этом ip-адрес сетевого узла должен создаваться с помощью функции ip_address().


import ipaddress
import subprocess


def host_ping(hosts):
    for i in hosts:
        # ipv4 = ipaddress.ip_address(i)
        res = subprocess.Popen(['ping', str(i)], stdout=subprocess.PIPE)
        result = res.stdout.read().decode('cp866')
        if '(0% потерь)' in result:
            print('Узел доступен')
        else:
            print('Узел недоступен')
        # print(result)


hosts = ['yandex.ru', 'youtube.com', '0.0.0.1']
host_ping(hosts)

# До конца так и не понял последнее условие с созданием ip-адреса сетевого узла через функцию ip_address(). 