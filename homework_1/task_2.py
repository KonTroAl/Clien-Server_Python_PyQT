# task 2
# Написать функцию host_range_ping() для перебора ip-адресов из заданного диапазона. Меняться должен только последний октет каждого адреса.
# По результатам проверки должно выводиться соответствующее сообщение


import ipaddress
import subprocess


def host_range_ping(host, num):
    subnet = ipaddress.ip_network(host)
    subnet_list = list(subnet.hosts())
    for i in range(num):
        response = subprocess.Popen(['ping', str(subnet_list[i])], stdout=subprocess.PIPE)
        result = response.stdout.read().decode('cp866')
        if '(0% потерь)' in result:
            print('Узел доступен')
        else:
            print('Узел недоступен')


hosts = '80.0.1.0/28'
num = 3
host_range_ping(hosts, num)
