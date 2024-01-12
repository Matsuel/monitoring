#!/bin/bash

if [ "$EUID" -ne 0 ]
    then echo "Veuillez lancer init en tant que root"
    exit
fi

mkdir -p /var/log/monit
mkdir -p /etc/monit/conf.d
mkdir -p /var/monit

# Change la propriété des dossiers à l'utilisateur actuellement connecté
chown -R $SUDO_USER:$SUDO_USER /var/log/monit
chown -R $SUDO_USER:$SUDO_USER /etc/monit/conf.d
chown -R $SUDO_USER:$SUDO_USER /var/monit

# Copie le fichier config.json dans le dossier /etc/monit/conf.d
cp config.json /etc/monit/conf.d/
cp monit.service /etc/systemd/system/
cp monit.timer /etc/systemd/system/