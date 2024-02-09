# Systeme de monitoring en python

<img src="./assets/api.svg" width="200px" /><img src="./assets/flask.svg" width="200px" /><img src="./assets/monitoring.svg" width="200px" /><img src="./assets/python.svg" width="200px" />

## Installation du service sur votre machine:

```bash
git clone https://github.com/Matsuel/monitoring
```

**Ensuite rendez-vous dans le dossier monitoring**

```bash
cd
cd monitoring
```

**Ajouter la permission d'être exécuté au fichier init.sh**

```bash
sudo chmod +x init.sh
```

**Puis lancer ce script qui vous installera et configurera tous les dossiers et fichiers nécessaires**

```bash
sudo bash init.sh
```

## Consultation des rapports 

**Si vous souhaitez consulter les rapports créés par ce service vous pouvez soit les consulter en brut**

```bash
ls /var/monit
```

**Soit les consultés en utilisant l'api python disponible dans le dossier monitoring**

```bash
python monit_api.py -p le-port-que-vous-voulez -a l'adresse-de-votre-machine
```

**Puis rendez-vous sur votre navigateur web pour consulter les rapports [Là](http://l'adresse-de-votre-machine:le-port-que-vous-voulez)**

## Utilisation de l'api

**Au démarrage de l'api sur votre navigateur vous arrivez sur une page de documentation qui vous montre comment l'utiliser et vous pourrez donc la tester avant de l'utiliser pour créer un site web de monitoring ou autre**

### Routes disponibles:

<ol>
<li> <strong>/reports</strong> : Renvoie tous les rapports dans la limite de 40 afin d'éviter certains bugs. Ces rapports seront au format json</li>

<li> <strong>/reports/avg/hours</strong> : Renvoie la moyenne de l'utilisation du cpu, de la mémoire ram le tout dans un json</li>

<li> <strong>/reports/last</strong> : Renvoie le dernier au format json avec toutes les informations récupérées</li>

<li> <strong>/reports/list</strong> : Renvoie le nom de tous les rapports qui ont été créés</li>

<li> <strong>/reports/{ID}</strong> : Renvoie le contenu du rapport dont l'ID est passé en paramètre s'il existe sinon une erreur est renvoyée id.json ou id est accepté comme paramètre</li>

<li> <strong>/version</strong> : Renvoie la version de l'api sous forme de string</li>
</ol>

### Schéma JSON

#### Rapport :

```json
{
  "boot_time": "int",
  "cpu": "float",
  "date": "int",
  "disk_space": {
    "string": "float"
  },
  "id": "string",
  "memory": "int",
  "os": {
    "machine": "string",
    "node": "string",
    "processor": "string",
    "release": "string",
    "system": "string",
    "version": "string"
  },
  "ports": {
    "inUse": [
      "int"
    ],
    "notInUse": [
      "int"
    ]
  },
  "process": {
    "name": [
      "int"
    ],
  }
}
  
```

#### Liste des rapports : 

```json
{
    "reports": {
        "reportID :string"
    }
}
```

#### Version : 

```json
{
    "version": "string"
}
```