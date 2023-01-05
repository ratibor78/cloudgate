#! /usr/bin/env bash

## Installation script for Cloudgate 
## Oleksii Nizhegolenko 2022


WORKDIR=$(pwd)

echo ""
echo "Creating virtual ENV and installing all needed requirements"
sleep 1
python3 -m venv venv && source venv/bin/activate
pip3 install -r requirements.txt && deactivate

echo ""
echo "Installing Cloudgate systemd service"
sleep 1

while read line
do
    eval echo "$line"
done < "./cloudgate.service.template" > /lib/systemd/system/cloudgate.service

systemctl enable geostat.service

echo ""
echo "Please edit the settings.ini file and set parameters"
sleep 1
cp settings.ini.bak settings.ini

PS3="Select the editor please: "

select lng in Vi Nano Quit
do
    case $lng in
        "Vi")
           "${VISUAL:-"${EDITOR:-vi}"}" "settings.ini";;
           break;;
        "Nano")
           "${VISUAL:-"${EDITOR:-nano}"}" "settings.ini";;
           break;;
        "Quit")
           echo "Please don't forget to edit settings.ini before starting the service"
           break;;
        *)
           echo "Ooops";;
    esac
done

echo ""
echo "The Cloudgate was installed successfully"
echo "Run 'systemctl start cloudgate.service'"
echo "Good luck!"
