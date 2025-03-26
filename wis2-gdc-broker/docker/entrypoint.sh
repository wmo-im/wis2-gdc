#!/bin/sh

USERNAME=`echo $WIS2_GDC_BROKER_URL |awk -F/ '{print $3}' | awk -F@ '{print $1}' | awk -F: '{print $1}'`
PASSWORD=`echo $WIS2_GDC_BROKER_URL |awk -F/ '{print $3}' | awk -F@ '{print $1}' | awk -F: '{print $2}'`

echo "Setting mosquitto authentication"

echo "USERNAME: $USERNAME"
echo "PASSWORD: $PASSWORD"

if [ ! -e "/mosquitto/config/password.txt" ]; then
    echo "Adding wis2-gdc users to mosquitto password file"
    mosquitto_passwd -b -c /mosquitto/config/password.txt $USERNAME $PASSWORD
    mosquitto_passwd -b /mosquitto/config/password.txt everyone everyone
    chmod 644 /mosquitto/config/password.txt
else
    echo "Mosquitto password file already exists. Skipping wis2-gdc user addition."
fi

if [ -e "/mosquitto/config/certs/tls.crt" ] && [ -e "/mosquitto/config/certs/tls.key" ] && [ -e "/mosquitto/config/certs/ca.crt" ] ; then
    echo "Adding Mosquitto SSL information from /mosquitto/config/mosquitto-ssl.inc"
    cat /mosquitto/config/mosquitto-ssl.inc >> /mosquitto/config/mosquitto.conf
fi

sed -i "s#_USERNAME#$USERNAME#" /mosquitto/config/acl.conf

/usr/sbin/mosquitto -c /mosquitto/config/mosquitto.conf
