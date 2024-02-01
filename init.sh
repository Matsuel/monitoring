#!/bin/bash

if [ "$EUID" -ne 0 ]
    then echo "Veuillez lancer init en tant que root"
    exit
fi

# Install python3 and pip3 if not installed
if ! [ -x "$(command -v python3)" ]; then
    echo 'Error: python is not installed.' >&2
    dnf install python3 -y
    echo "Python3 installed"
fi

if ! [ -x "$(command -v pip3)" ]; then
    echo 'Error: pip is not installed.' >&2
    dnf install python3-pip -y
    echo "Pip3 installed"
fi


# Installations des dépendances
pip3 install psutil Flask swagger-ui-py > /dev/null 2>&1
echo "Dependencies installed"

# Création d'un utilisateur monit qui sera utilisé pour lancer le script monit.py
useradd monit

# Création des dossiers nécessaires
mkdir -p /var/log/monit /etc/monit/conf.d /var/monit

# Copie le fichier config.json dans le dossier /etc/monit/conf.d
cp config.json /etc/monit/conf.d/
cp monit.service monit.timer /etc/systemd/system/
cp monit.py /var/monit/

# Change la propriété des dossiers à l'utilisateur actuellement connecté afin qu'il puisse écrire les rapports dedans
chown -R monit:monit /var/log/monit
chown -R monit:monit /etc/monit/conf.d
chown -R monit:monit /var/monit

echo "Installation done"

# Démarrage automatique de monit dès le démarrage de la machine et démarrage du timer maintenant afin qu'il commence à créer des rapports
systemctl daemon-reload
systemctl enable monit.timer
systemctl start monit.timer

echo "Monit started"