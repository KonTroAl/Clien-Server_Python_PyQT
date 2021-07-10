# task 3
# Написать функцию host_range_ping_tab(), возможности которой основаны на функции из примера 2.
# Но в данном случае результат должен быть итоговым по всем ip-адресам, представленным в табличном формате (использовать модуль tabulate).

import ipaddress
import subprocess
from tabulate import tabulate


def host_range_ping_tab(host, number):
    reachable = []
    unreachable = []
    f_dict = {'Reachable': reachable, 'Unreachable': unreachable}
    subnet = ipaddress.ip_network(host)
    subnet_list = list(subnet.hosts())
    for i in range(number):
        response = subprocess.Popen(['ping', str(subnet_list[i])], stdout=subprocess.PIPE)
        result = response.stdout.read().decode('cp866')
        if '(0% потерь)' in result:
            reachable.append(str(subnet_list[i]))
        else:
            unreachable.append(str(subnet_list[i]))
    print(tabulate(f_dict, headers='keys', tablefmt='pipe'))


hosts = '80.0.1.0/28'
num = 3
host_range_ping_tab(hosts, num)
