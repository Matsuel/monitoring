import psutil
import time
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--check", help="Check la valeur du cpu, de la ram, des ports et de l'espace disque et renvoie un json")
parser.add_argument("--list", help="Renvoie la liste des rapport json")
parser.add_argument("--get_last", help="Renvoie le dernier rapport json")
parser.add_argument("--get_avg", nargs=1, help="Calcule les valeurs moyennes des X dernières heures de chaque ressource")
args = parser.parse_args()


def get_config()->dict:
    with open("config.json", "r") as f:
        return json.load(f)



def get_cpu_usage()->float:
    return psutil.cpu_percent(1)

def get_memory_usage()->float:
    # return psutil.virtual_memory()
    return round(psutil.virtual_memory()[3]/psutil.virtual_memory()[0]*100, 1)

print(f"Memory usage {get_memory_usage()}")

def get_disk_space()->dict:
    rep = {}
    partitions = psutil.disk_partitions()
    for partition in partitions:
        partiton_infos = psutil.disk_usage(partition.mountpoint)
        rep[partition.mountpoint] = round(partiton_infos[1]/partiton_infos[0]*100, 1)
    return rep

print(f"Disk usage {get_disk_space()}")

def boot_time()->float:
    return f"{int(time.time() - psutil.boot_time())//60//60} h {int(time.time() - psutil.boot_time())//60%60} min"

print(f"Boot time {boot_time()}")

def get_used_ports()->list:
    useds_ports = psutil.net_connections()
    rep=[]
    for port in useds_ports:
        rep.append(port[3][1])
    return rep

print(f"Used ports {get_used_ports()}")

def not_in_list(liste:list, element)->bool:
    return element not in liste

def get_ports_open(ports:list)->dict:
    used_ports = get_used_ports()
    rep={}
    for port in ports:
        rep[port] = not_in_list(used_ports, port)
    return rep

print(f"Ports {get_ports_open(get_config()['portsRange'])}")

print(f"Config {get_config()}")