#!/bin/bash

# Vérifie si le script est exécuté en tant que sudo
if [ "$EUID" -ne 0 ]
    then echo "Veuillez exécuter en tant que sudo"
    exit
fi

# Crée les dossiers s'ils n'existent pas
mkdir -p /var/log/monit
mkdir -p /etc/monit/conf.d
mkdir -p /var/monit

# Change la propriété des dossiers à l'utilisateur actuellement connecté
chown -R $SUDO_USER:$SUDO_USER /var/log/monit
chown -R $SUDO_USER:$SUDO_USER /etc/monit/conf.d
chown -R $SUDO_USER:$SUDO_USER /var/monit

# Crée le fichier monit.log s'il n'existe pas
touch /var/log/monit/monit.log

# Copie le fichier config.json dans le dossier /etc/monit/conf.d
cp config.json /etc/monit/conf.d/