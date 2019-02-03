#!/usr/bin/env bash
rsync -av --delete -e "ssh -i /home/brutkowski/klucze/EU-WEST.pem" ./src ubuntu@ec2-18-202-228-162.eu-west-1.compute.amazonaws.com:/home/ubuntu/inzynierka
rsync -av --delete -e "ssh -i /home/brutkowski/klucze/EU-WEST.pem" ./data ubuntu@ec2-18-202-228-162.eu-west-1.compute.amazonaws.com:/home/ubuntu/inzynierka