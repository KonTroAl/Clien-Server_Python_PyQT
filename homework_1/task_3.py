# task 3
# Написать функцию host_range_ping_tab(), возможности которой основаны на функции из примера 2.
# Но в данном случае результат должен быть итоговым по всем ip-адресам, представленным в табличном формате (использовать модуль tabulate).

import ipaddress
import subprocess
from tabulate import tabulate


def host_range_ping_tab(hos, number):
    a = []
    reachable = []
    unreachable = []
    f_dict = {'Reachable': reachable, 'Unreachable': unreachable}
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
            reachable.append(str(i))
        else:
            unreachable.append(str(i))
    print(tabulate(f_dict, headers='keys', tablefmt='pipe'))


hosts = '80.0.1.1'

num = 3

host_range_ping_tab(hosts, num)
