#!/bin/bash

if [ "$EUID" -ne 0 ]
    then echo "Veuillez lancer init en tant que root"
    exit
fi

# Install python3 and pip3 if not installed
if ! [ -x "$(command -v python3)" ]; then
    echo 'Error: python is not installed.' >&2
    sudo apt install python3 python3-pip
    echo "Python3 installed"
    exit 1
fi

# Install python libraries
pip3 install psutil
pip3 install Flask
pip3 install flask-swagger-ui

mkdir -p /var/log/monit
mkdir -p /etc/monit/conf.d
mkdir -p /var/monit

# Change la propriété des dossiers à l'utilisateur actuellement connecté afin qu'il puisse écrire les rapports dedans
chown -R $SUDO_USER:$SUDO_USER /var/log/monit
chown -R $SUDO_USER:$SUDO_USER /etc/monit/conf.d
chown -R $SUDO_USER:$SUDO_USER /var/monit

# Copie le fichier config.json dans le dossier /etc/monit/conf.d
cp config.json /etc/monit/conf.d/
cp monit.service /etc/systemd/system/
cp monit.timer /etc/systemd/system/

# Démarrage automatique de monit dès le démarrage de la machine et démarrage du timer maintenant afin qu'il commence à créer des rapports
systemctl daemon-reload
systemctl enable monit.timer
systemctl start monit.timer