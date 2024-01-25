import psutil
import time
import json
import argparse
import uuid
import os
import logging
from datetime import datetime

def get_config()->dict:
    with open(f"{directory_config}/config.json", "r") as f:
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

def boot_time()->int:
    return int(psutil.boot_time())

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
    use_ports=[]
    notInUse_ports=[]
    for port in ports:
        if port in used_ports:
            use_ports.append(port)
        else:
            notInUse_ports.append(port)
    rep["inUse"] = use_ports
    rep["notInUse"] =   notInUse_ports
    return rep

def get_process_list()->dict:
    process = psutil.process_iter()
    process_dict = {}
    for p in process:
        if p.name() in process_dict.keys():
            process_dict[p.name()].append(p.pid)
        elif p.name() != "":
            process_dict[p.name()] = [p.pid]
    return process_dict


def create_report()->dict:
    return {
        "id": str(uuid.uuid4()),
        "date": int(time.time()),
        "boot_time": boot_time(),
        "cpu": get_cpu_usage(),
        "memory": get_memory_usage(),
        "disk_space": get_disk_space(),
        "ports": get_ports_open(),
        "process": get_process_list()
    }

def create_report_directory(directory:str):
    if not os.path.exists(directory):
        os.mkdir(directory)

def save_report(report:dict,directory:str):
    create_report_directory(directory)
    with open(f"{directory}/{report['id']}.json", "w") as f:
        json.dump(report, f)
    log(f"Report {report['id']} saved")

def get_all_reports(directory:str)->list:
    create_report_directory(directory)
    log(f"Get all reports")
    return os.listdir(directory)

def get_all_reports_content(directory:str)->list:
    create_report_directory(directory)
    rep=[]
    for file in os.listdir(directory):
        with open(f"{directory}/{file}", "r") as f:
            rep.append(json.load(f))
    return rep

def get_last_report(directory:str)->dict:
    create_report_directory(directory)
    last=None
    for file in os.listdir(directory):
        if last is None:
            last = file
        elif os.path.getmtime(f"{directory}/{file}") > os.path.getmtime(f"{directory}/{last}"):
            last = file
    with open(f"{directory}/{last}", "r") as f:
        content = json.load(f)
        log(f"Get last report {content['id']}")
        return content
    
def get_report(name:str, directory:str)->dict:
    create_report_directory(directory)
    if os.path.exists(f"{directory}/{name}"):
        with open(f"{directory}/{name}", "r") as f:
            return json.load(f)
    else:
        log(f"Report {name} doesn't exist")
        return None
    
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
    if rep is not None:
        rep["cpu"] /= len(reports)
        rep["memory"] /= len(reports)
        return rep
    else:
        return None

directory = "/var/monit" if os.name == "posix" else "./monit"
directory_log = "/var/log/monit" if os.name == "posix" else "./log"
directory_config = "/etc/monit/conf.d" if os.name == "posix" else "."

def create_config_directory(directory:str):
    if not os.path.exists(directory):
        os.mkdir(directory)

def create_log_file():
    if not os.path.exists(directory_log):
        os.mkdir(directory_log)
    logging.basicConfig(filename=f"{directory_log}/monit.log", level=logging.INFO, format='%(asctime)s %(message)s')

def log(message:str):
    logging.info(message)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # parser.add_argument("--check","-c",action="store_true", help="Check la valeur du cpu, de la ram, des ports et de l'espace disque et renvoie un json")
    # parser.add_argument("--list","-l", action="store_true", help="Renvoie la liste des rapport json")
    # parser.add_argument("--get_last", action="store_true", help="Renvoie le dernier rapport json")
    # parser.add_argument("--get_avg", nargs=1, help="Calcule les valeurs moyennes des X dernières heures de chaque ressource")
    # args = parser.parse_args()

    # parser.add_argument("command", help="Commande à executer", choices=["check", "list", "get"])
    # parser.add_argument("parameter", help="Le paramètre de la commande", nargs='*', default='')
    # args = parser.parse_args()

    # create_config_directory(directory)
    # create_log_file()
    # if args.command == "check":
    #     save_report(create_report(), directory)
    # elif args.command == "list":
    #     print(get_all_reports(directory))
    # elif args.command == "get":
    #     if args.parameter[0] == "last":
    #         print(get_last_report(directory))
    #     elif args.parameter[0] == "avg":
    #         print(get_avg_of_report(int(args.parameter[1]), directory))
    #     elif args.parameter[0] == "name":
    #         if (args.parameter[1] == ""):
    #             print("Veuillez spécifier le nom du rapport")
    #         elif (args.parameter[1].endswith(".json")):
    #             print(get_report(args.parameter[1], directory))
    #         else:
    #             print(get_report(args.parameter[1]+".json", directory))
    # else:
    #     print("Cette commande n'existe pas ! Les commandes disponibles sont : check, list, get voir plus d'infos avec --help")