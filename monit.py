"""
Monit est un outil de monitoring de serveur, il permet
de récupérer des informations sur le serveur et de les
sauvegarder dans un fichier json.
"""
from time import time
from uuid import uuid4
from json import load, dump
from argparse import ArgumentParser
from os import path, mkdir, listdir, name
import platform
import logging
import psutil


def get_config()->dict:
    """
    Renvoie le contenu du fichier config.json
    """
    with open(f"{DIRECTORY_CONFIG}/config.json", "r", encoding="utf-8") as f:
        return load(f)

def get_cpu_usage()->float:
    """
    Renvoie l'utilisation du cpu en pourcentage
    """
    return psutil.cpu_percent(1)

def get_memory_usage()->float:
    """
    Renvoie l'utilisation de la ram en pourcentage
    """
    return round(psutil.virtual_memory()[3]/psutil.virtual_memory()[0]*100, 1)

def get_disk_space()->dict:
    """
    Renvoie l'utilisation de l'espace disque en pourcentage
    """
    rep = {}
    partitions = psutil.disk_partitions()
    for partition in partitions:
        partiton_infos = psutil.disk_usage(partition.mountpoint)
        rep[partition.mountpoint] = round(partiton_infos[1]/partiton_infos[0]*100, 1)
    return rep

def boot_time()->int:
    """
    Renvoie le temps de démarrage en timestamp
    """
    return int(psutil.boot_time())

def get_used_ports()->list:
    """
    Renvoie la liste des ports utilisés
    """
    useds_ports = psutil.net_connections()
    rep=[]
    for port in useds_ports:
        rep.append(port[3][1])
    return rep

def get_ports_open()->dict:
    """
    Renvoie la liste des ports ouverts et fermés en 
    fonction des ports renseignés dans le fichier config.json
    """
    used_ports = get_used_ports()
    ports = get_config()["portsRange"]
    rep={}
    use_ports=[]
    not_in_use_ports=[]
    for port in ports:
        if port in used_ports:
            use_ports.append(port)
        else:
            not_in_use_ports.append(port)
    rep["inUse"] = use_ports
    rep["notInUse"] =   not_in_use_ports
    return rep

def get_process_list()->dict:
    """
    Renvoie la liste des processus en cours
    """
    process = psutil.process_iter()
    process_dict = {}
    for p in process:
        process_name= p.name().replace(".exe", "").capitalize()
        if process_name in process_dict:
            process_dict[process_name].append(p.pid)
        else:
            process_dict[process_name] = [p.pid]
    return process_dict

def get_os_infos()->dict:
    """
    Renvoie les informations sur l'OS
    """
    system_info = platform.uname()
    return {
        "system": system_info.system,
        "node": system_info.node,
        "release": system_info.release,
        "version": system_info.version,
        "machine": system_info.machine,
        "processor": system_info.processor
    }


def create_report()->dict:
    """
    Crée un rapport
    """
    return {
        "id": str(uuid4()),
        "date": int(time()),
        "boot_time": boot_time(),
        "cpu": get_cpu_usage(),
        "os": get_os_infos(),
        "memory": get_memory_usage(),
        "disk_space": get_disk_space(),
        "ports": get_ports_open(),
        "process": get_process_list()
    }

def create_report_directory(directory:str):
    """
    Crée le dossier de stockage des rapports
    """
    if not path.exists(directory):
        mkdir(directory)

def save_report(report:dict,directory:str):
    """
    Sauvegarde un rapport dans le dossier de stockage
    """
    create_report_directory(directory)
    with open(f"{directory}/{report['id']}.json", "w", encoding="utf-8") as f:
        dump(report, f)
    log(f"Report {report['id']} saved")

def get_all_reports(directory:str)->list:
    """
    Renvoie la liste des rapports
    """
    create_report_directory(directory)
    log("Get all reports")
    return [report for report in listdir(directory) if report.endswith(".json")]

def get_all_reports_content(directory:str)->list:
    """
    Renvoie la liste des rapports
    """
    create_report_directory(directory)
    rep=[]
    for i,report in enumerate(get_all_reports(directory)):
        print(report)
        with open(f"{directory}/{report}", "r", encoding="utf-8") as f:
            rep.append(load(f))
    return rep

def get_last_report(directory:str)->dict:
    """
    Renvoie le dernier rapport
    """
    create_report_directory(directory)
    last=None
    for file in listdir(directory):
        if last is None:
            last = file
        elif path.getmtime(f"{directory}/{file}") > path.getmtime(f"{directory}/{last}"):
            last = file
    with open(f"{directory}/{last}", "r", encoding="utf-8") as f:
        content = load(f)
        log(f"Get last report {content['id']}")
        return content

def get_report(report_name:str, directory:str)->dict:
    """
    Renvoie un rapport en fonction de son nom
    """
    create_report_directory(directory)
    if path.exists(f"{directory}/{report_name}"):
        with open(f"{directory}/{report_name}", "r", encoding="utf-8") as f:
            return load(f)
    else:
        log(f"Report {report_name} doesn't exist")
        return None

def get_reports_younger_than(hours:int, directory:str)->list:
    """
    Renvoie la liste des rapports plus jeunes que X heures
    """
    create_report_directory(directory)
    rep=[]
    for file in listdir(directory):
        if time() - path.getmtime(f"{directory}/{file}") < hours*60*60 and file.endswith(".json"):
            rep.append(file)
    return rep

def get_avg_of_report(hours:int,directory:str)->dict:
    """
    Renvoie la moyenne des valeurs des rapports plus jeunes que X heures
    """
    reports=get_reports_younger_than(hours, directory)
    log(f"Get avg of {hours} last hours")
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
    return None

DIRECTORY = "/var/monit" if name == "posix" else "./monit"
DIRECTORY_LOG = "/var/log/monit" if name == "posix" else "./log"
DIRECTORY_CONFIG = "/etc/monit/conf.d" if name == "posix" else "."

def create_config_directory(directory:str):
    """
    Crée le dossier de configuration
    """
    if not path.exists(directory):
        mkdir(directory)

def create_log_file():
    """
    Crée le fichier de log
    """
    if not path.exists(DIRECTORY_LOG):
        mkdir(DIRECTORY_LOG)
    logging.basicConfig(
        filename=f"{DIRECTORY_LOG}/monit.log", level=logging.INFO, format='%(asctime)s %(message)s')

def log(message:str):
    """
    Log un message
    """
    logging.info(message)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("command", help="Commande à executer", choices=["check", "list", "get"])
    parser.add_argument("parameter", help="Le paramètre de la commande", nargs='*', default='')
    args = parser.parse_args()

    create_config_directory(DIRECTORY)
    create_log_file()
    if args.command == "check":
        save_report(create_report(), DIRECTORY)
    elif args.command == "list":
        print(get_all_reports(DIRECTORY))
    elif args.command == "get":
        if args.parameter[0] == "last":
            print(get_last_report(DIRECTORY))
        elif args.parameter[0] == "avg":
            print(get_avg_of_report(int(args.parameter[1]), DIRECTORY))
        elif args.parameter[0] == "name":
            if args.parameter[1] == "" :
                print("Veuillez spécifier le nom du rapport")
            elif args.parameter[1].endswith(".json") :
                print(get_report(args.parameter[1], DIRECTORY))
            else:
                print(get_report(args.parameter[1]+".json", DIRECTORY))
    else:
        print("""
            Cette commande n'existe pas ! 
            Les commandes disponibles sont : 
            check, list, get voir plus d'infos avec --help
            """)
