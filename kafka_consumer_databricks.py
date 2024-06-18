from confluent_kafka import Consumer
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import json
import time

# Configuración de InfluxDB
influxdb_url = "#Cambiar por la URL de su instancia de InfluxDB"
influxdb_token = "#Cambiar por su token de InfluxDB"
influxdb_org = "#Cambiar por su organización de InfluxDB"
influxdb_bucket = "#Cambiar por el nombre de su bucket de InfluxDB"

# Crear un cliente de InfluxDB
client = InfluxDBClient(url=influxdb_url, token=influxdb_token, org=influxdb_org)
write_api = client.write_api(write_options=SYNCHRONOUS)

# Configurar el consumidor de Kafka
c = Consumer({
    'bootstrap.servers': '#ip:9092,#ip:9093,#ip:9094',
    'group.id': 'python-consumer',
    'auto.offset.reset': 'earliest'
})

print('Kafka Consumer has been initiated...')
print('Available topics to consume: ', c.list_topics().topics)
c.subscribe(['logs'])


while True:
    try:
        msg = c.poll(1.0)  # timeout
        if msg is None:
            continue
        if msg.error():
            print('Error: {}'.format(msg.error()))
            continue
        
        data = msg.value().decode('utf-8')
        print(data)
        
        # Parsear el mensaje JSON
        data_json = json.loads(data)
        
        # Crear un punto de datos para InfluxDB
        point = Point("logs") \
            .tag("user_id", data_json["user_id"]) \
            .field("user_name", data_json["user_name"]) \
            .tag("platform", data_json["platform"]) \
            .tag("browser", data_json["browser"]) \
            .tag("device", data_json["device"]) \
            .field("user_address", data_json["user_address"]) \
            .field("time_spent", data_json["time_spent"]) \
            .field("last_login", data_json["last_login"]) \
            .field("signup_at", data_json["signup_at"])
        
        # Escribir el punto en InfluxDB
        write_api.write(bucket=influxdb_bucket, org=influxdb_org, record=point)
        
        # Esperar 2 segundos antes de enviar la siguiente solicitud
        time.sleep(5)
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Reconectando...")

c.close()
