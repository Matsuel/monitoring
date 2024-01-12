#!/bin/bash

# Vérifie si le script est exécuté en tant que sudo
if [ "$EUID" -ne 0 ]
    then echo "Veuillez exécuter en tant que sudo"
    exit
fi

# Crée les dossiers s'ils n'existent pas
mkdir -p /var/log/monit
mkdir -p /etc/monit/conf.d

# Crée le fichier monit.log s'il n'existe pas
touch /var/log/monit/monit.log

# Copie le fichier config.json dans le dossier /etc/monit/conf.d
cp config.json /etc/monit/conf.d/