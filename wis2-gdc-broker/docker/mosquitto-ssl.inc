## TLS/SSL settings
## uncomment if using SSL

# MQTT Listener
listener 8883
protocol mqtt

# cert and key files 
cafile /mosquitto/config/certs/ca.crt
certfile /mosquitto/config/certs/tls.crt
keyfile /mosquitto/config/certs/tls.key
