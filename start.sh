#!/bin/bash

echo "************************************************Démarrage du programme************************************************"

# echo "*************Démarrage des containers*************"
docker-compose up -d

sleep 10

cd /home/mandiaye/logstash-8.6.0-linux-x86_64/logstash-8.6.0/bin
echo "************************************************Démarrage du pipeline************************************************"
./logstash -f /home/mandiaye/LORIA/essaieTikaFR/logstash/pipeline/mongo.conf &

sleep 30

echo "************************************************Insertion des documents dans MongoDB************************************************"
/bin/python3 /home/mandiaye/LORIA/essaieTika/script/Mongo.py