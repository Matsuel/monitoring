import psutil
import time
import json
import argparse
import uuid
import os

parser = argparse.ArgumentParser()
parser.add_argument("--check","-c",action="store_true", help="Check la valeur du cpu, de la ram, des ports et de l'espace disque et renvoie un json")
parser.add_argument("--list","-l", action="store_true", help="Renvoie la liste des rapport json")
parser.add_argument("--get_last", action="store_true", help="Renvoie le dernier rapport json")
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

def get_disk_space()->dict:
    rep = {}
    partitions = psutil.disk_partitions()
    for partition in partitions:
        partiton_infos = psutil.disk_usage(partition.mountpoint)
        rep[partition.mountpoint] = round(partiton_infos[1]/partiton_infos[0]*100, 1)
    return rep

def boot_time()->float:
    return f"{int(time.time() - psutil.boot_time())//60//60} h {int(time.time() - psutil.boot_time())//60%60} min"

def get_used_ports()->list:
    useds_ports = psutil.net_connections()
    rep=[]
    for port in useds_ports:
        rep.append(port[3][1])
    return rep

def not_in_list(liste:list, element)->bool:
    return element not in liste

def get_ports_open()->dict:
    used_ports = get_used_ports()
    ports = get_config()["portsRange"]
    rep={}
    for port in ports:
        rep[port] = not_in_list(used_ports, port)
    return rep

def create_report()->dict:
    return {
        "id": str(uuid.uuid4()),
        "date": time.strftime("%d/%m/%Y %H:%M:%S"),
        "boot_time": boot_time(),
        "cpu": get_cpu_usage(),
        "memory": get_memory_usage(),
        "disk_space": get_disk_space(),
        "ports": get_ports_open()
    }

def create_report_directory():
    if not os.path.exists("/var/monit"):
        os.mkdir("/var/monit")

def save_report(report:dict):
    create_report_directory()
    with open(f"./monit/{report['id']}.json", "w") as f:
        json.dump(report, f, indent=4)

def get_all_reports()->list:
    create_report_directory()
    return os.listdir("/var/monit")

def get_last_report()->dict:
    create_report_directory()
    last=None
    for file in os.listdir("/var/monit"):
        if last is None:
            last = file
        elif os.path.getmtime(f"/var/monit/{file}") > os.path.getmtime(f"/var/monit/{last}"):
            last = file
    with open(f"/var/monit/{last}", "r") as f:
        return json.load(f)
        

print(args)

if args.check:
    save_report(create_report())
elif args.list:
    print(get_all_reports())
elif args.get_last:
    print(get_last_report())
