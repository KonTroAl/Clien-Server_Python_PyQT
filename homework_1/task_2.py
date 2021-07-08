# task 2
# Написать функцию host_range_ping() для перебора ip-адресов из заданного диапазона. Меняться должен только последний октет каждого адреса.
# По результатам проверки должно выводиться соответствующее сообщение


hosts = '80.0.1.1'

import ipaddress
import subprocess


def host_range_ping(hos, number):
    a = []
    ipv4 = ipaddress.ip_address(hos)
    a.append(str(ipv4))
    res = ipv4 + 1
    a.append(str(res))
    for i in range(number - 2):
        res = res + 1
        number = number - 1
        a.append(str(res))
    for i in a:
        response = subprocess.Popen(['ping', str(i)], stdout=subprocess.PIPE)
        result = response.stdout.read().decode('cp866')
        if '(0% потерь)' in result:
            print('Узел доступен')
        else:
            print('Узел недоступен')


# val = input('Введите начальный ip-адрес: ')
# num = input('Введите количество прослушиваемых ip-адресов: ')
num = 3

host_range_ping(hosts, num)
