import psutil
import time
import json
import argparse
import uuid
import os
import logging

parser = argparse.ArgumentParser()
# parser.add_argument("--check","-c",action="store_true", help="Check la valeur du cpu, de la ram, des ports et de l'espace disque et renvoie un json")
# parser.add_argument("--list","-l", action="store_true", help="Renvoie la liste des rapport json")
# parser.add_argument("--get_last", action="store_true", help="Renvoie le dernier rapport json")
# parser.add_argument("--get_avg", nargs=1, help="Calcule les valeurs moyennes des X dernières heures de chaque ressource")
# args = parser.parse_args()

parser.add_argument("command", help="Commande à executer", choices=["check", "list", "get"])
parser.add_argument("parameter", help="Le paramètre de la commande", nargs='*', default='')
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

def create_report_directory(directory:str):
    if not os.path.exists(directory):
        os.mkdir(directory)

def save_report(report:dict,directory:str):
    create_report_directory(directory)
    with open(f"{directory}/{report['id']}.json", "w") as f:
        json.dump(report, f, indent=4)
    log(f"Report {report['id']} saved")

def get_all_reports(directory:str)->list:
    create_report_directory(directory)
    log(f"Get all reports")
    return os.listdir(directory)

def get_last_report(directory:str)->dict:
    create_report_directory(directory)
    last=None
    for file in os.listdir(directory):
        if last is None:
            last = file
        elif os.path.getmtime(f"{directory}/{file}") > os.path.getmtime(f"{directory}/{last}"):
            last = file
    with open(f"{directory}/{last}", "r") as f:
        log(f"Get last report {json.load(f)['id']}")
        return json.load(f)
    
def get_report(name:str, directory:str)->dict:
    create_report_directory(directory)
    with open(f"{directory}/{name}", "r") as f:
        return json.load(f)
    
def get_reports_younger_than(hours:int, directory:str)->list:
    create_report_directory(directory)
    rep=[]
    for file in os.listdir(directory):
        if time.time() - os.path.getmtime(f"{directory}/{file}") < hours*60*60:
            rep.append(file)
    return rep    

def get_avg_of_report(hours:int,directory:str)->dict:
    reports=get_reports_younger_than(hours, directory)
    log(f"Get avg of {hours} last hours")
    # return reports
    rep=None

    for report in reports:
        r=get_report(report, directory)
        if rep is None:
            rep = r
        else:
            rep["cpu"] += r["cpu"]
            rep["memory"] += r["memory"]
    rep["cpu"] /= len(reports)
    rep["memory"] /= len(reports)
    return rep

directory = "/var/monit"

def create_config_directory(directory:str):
    if not os.path.exists(directory):
        os.mkdir(directory)

def create_log_file():
    if not os.path.exists("/var/log/monit"):
        os.mkdir("/var/log/monit")
    logging.basicConfig(filename='/var/log/monit/monit.log', level=logging.INFO, format='%(asctime)s %(message)s')

def log(message:str):
    logging.info(message)


if __name__ == "__main__":
    create_config_directory(directory)
    create_log_file()
    if args.command == "check":
        save_report(create_report(), directory)
    elif args.command == "list":
        print(get_all_reports(directory))
    elif args.command == "get":
        if args.parameter[0] == "last":
            print(get_last_report(directory))
        elif args.parameter[0] == "avg":
            print(get_avg_of_report(int(args.parameter[1]), directory))


# if args.check:
#     save_report(create_report(), directory)
# elif args.list:
#     print(get_all_reports(directory))
# elif args.get_last:
#     print(get_last_report(directory))
# elif args.get_avg:
#     print(get_avg_of_report(int(args.get_avg[0]), directory))