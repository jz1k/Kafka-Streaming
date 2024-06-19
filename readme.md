# Kafka Streaming Project.

## Contenido
1. [Visión General del Proyecto](#visión-general-del-proyecto)
2. [Arquitectura](#arquitectura)
3. [Ejecutar el Proyecto](#ejecutar-el-proyecto)

## Visión General del Proyecto

Este proyecto se centra en el uso de Apache Kafka para el procesamiento de streams en tiempo real. Se utilizan varias tecnologías como Kafka, Spark Streaming e InfluxDB para crear una arquitectura de análisis de datos en tiempo real. Los datos se generan a través de un productor de Kafka y se consumen con Spark Streaming. Luego, los datos se envían a InfluxDB para su almacenamiento y visualización en Grafana.

## Arquitectura

La arquitectura del proyecto se compone de los siguientes componentes:

- **Apache Kafka**: Plataforma de streaming distribuido que permite publicar y suscribirse a flujos de datos en tiempo real.
- **Spark Streaming**: Extensión de Spark que permite el procesamiento de flujos de datos en tiempo real.
- **InfluxDB**: Base de datos de series temporales utilizada para almacenar y visualizar datos de series temporales.
- **Grafana**: Plataforma de análisis y visualización de datos utilizada para crear paneles y gráficos interactivos.

## Ejecutar el Proyecto

1. **Iniciar Kafka en Docker con el siguiente docker-compose.yaml**:
     ```yaml
        version: '3'
        services:
        zookeeper:
            image: confluentinc/cp-zookeeper:7.0.1
            container_name: zookeeper
            ports:
            - "2181:2181"
            networks:
            - kafka-net
            restart: always
            environment:
            ZOOKEEPER_CLIENT_PORT: 2181
            ZOOKEEPER_TICK_TIME: 2000

        broker1:
            image: confluentinc/cp-kafka:7.0.1
            container_name: broker1
            depends_on:
            - zookeeper
            ports:
            - "29092:29092"
            - "9092:9092"
            networks:
            - kafka-net
            restart: always
            environment:
            KAFKA_BROKER_ID: 1
            KAFKA_ZOOKEEPER_CONNECT: 'zookeeper:2181'
            KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
            KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://broker1:29092,PLAINTEXT_HOST://48.217.73.18:9092
            KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:29092,PLAINTEXT_HOST://0.0.0.0:9092
            KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 3
            KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
            KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 3
            KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0

        broker2:
            image: confluentinc/cp-kafka:7.0.1
            container_name: broker2
            depends_on:
            - zookeeper
            ports:
            - "29093:29093"
            - "9093:9093"
            networks:
            - kafka-net
            restart: always
            environment:
            KAFKA_BROKER_ID: 2
            KAFKA_ZOOKEEPER_CONNECT: 'zookeeper:2181'
            KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
            KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://broker2:29093,PLAINTEXT_HOST://48.217.73.18:9093
            KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:29093,PLAINTEXT_HOST://0.0.0.0:9093
            KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 3
            KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
            KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 3
            KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0

        broker3:
            image: confluentinc/cp-kafka:7.0.1
            container_name: broker3
            depends_on:
            - zookeeper
            ports:
            - "29094:29094"
            - "9094:9094"
            networks:
            - kafka-net
            restart: always
            environment:
            KAFKA_BROKER_ID: 3
            KAFKA_ZOOKEEPER_CONNECT: 'zookeeper:2181'
            KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
            KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://broker3:29094,PLAINTEXT_HOST://48.217.73.18:9094
            KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:29094,PLAINTEXT_HOST://0.0.0.0:9094
            KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 3
            KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
            KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 3
            KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0

        kowl:
            image: quay.io/cloudhut/kowl
            depends_on:
            - broker1
            - broker2
            - broker3
            container_name: kowl
            ports:
            - "8080:8080"
            networks:
            - kafka-net
            restart: always
            environment:
            KAFKA_BROKERS: 'broker1:29092,broker2:29093,broker3:29094'

        networks:
        kafka-net:
            name: kafka-net-logs
            driver: bridge

2. **Crear un Tópico en Kafka**:
   ```sh
   docker-compose exec broker1 kafka-topics --create --topic logs --partitions 2 --replication-factor 3 --if-not-exists --bootstrap-server broker1:29092,broker2:29093,broker3:29094

3. **Iniciar el Productor de Kafka**:
![productor](https://github.com/jz1k/Kafka-Streaming/blob/main/capturas/prod.jpg?raw=true)
   - Navega al directorio del productor y ejecuta el script para enviar datos a Kafka.
     ```python
        import json
        import logging
        import random
        import time

        from confluent_kafka import Producer
        from faker import Faker

        fake = Faker()

        logging.basicConfig(format='%(asctime)s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            filename='producer.log',
                            filemode='w')

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        # Conectar a los tres brokers
        p = Producer({
            'bootstrap.servers': '#ip:9092,#ip:9093,#ip:9094'
        })

        print('Kafka Producer has been initiated...')

        def receipt(err, msg):
            if err is not None:
                print('Error: {}'.format(err))
            else:
                message = 'Produced message on topic {} with value of {}\n'.format(msg.topic(), msg.value().decode('utf-8'))
                logger.info(message)
                print(message)

        # Generar una lista de usuarios inicial
        users = []
        for _ in range(100):  # Cambia 100 según necesites
            user = {
                'user_id': fake.random_int(min=20000, max=100000),
                'user_name': fake.name(),
                'user_address': fake.street_address() + ' | ' + fake.city() + ' | ' + fake.country_code(),
                'platform': random.choice(['Mobile', 'Laptop', 'Tablet']),
                'browser': random.choice(['Chrome', 'Firefox', 'Safari', 'Edge', 'Opera']),
                'device': random.choice(['iOS', 'Android', 'Windows', 'Linux', 'MacOS']),
                'signup_at': str(fake.date_time_this_year())
            }
            users.append(user)

        def generate_message():
            user = random.choice(users)
            data = {
                'user_id': user['user_id'],
                'user_name': user['user_name'],
                'user_address': user['user_address'],
                'platform': user['platform'],
                'browser': user['browser'],
                'device': user['device'],
                'time_spent': fake.random_int(min=1, max=60),
                'last_login': str(fake.date_time_this_year()),
                'signup_at': user['signup_at']
            }
            return data

        def main():
            # while True:
            for i in range(400):
                data = generate_message()
                m = json.dumps(data)
                p.poll(1)
                p.produce('logs', m.encode('utf-8'), callback=receipt)
                p.flush()
                time.sleep(2)

        if __name__ == '__main__':
            main()

4. **Iniciar el Consumidor de Kafka con Spark Streaming para mandar la información a InfluxDB**:
![consumidor](https://github.com/jz1k/Kafka-Streaming/blob/main/capturas/cons.jpg?raw=true)
      ```python
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

## Ingesta de Datos en InfluxDB

Para visualizar los datos en InfluxDB, se ha configurado la base de datos para recibir los datos de Kafka. Se ha creado un bucket llamado `logs` y se ha conectado grafas para visualizar los datos en tiempo real.

![influxdb](https://github.com/jz1k/Kafka-Streaming/blob/main/capturas/influx.jpg?raw=true)

## Grafana Dashboard

Se ha creado un panel en Grafana para visualizar los datos en tiempo real. El panel muestra el tiempo que los usuarios pasan en la plataforma, el dispositivo que utilizan, el navegador que utilizan y muchos otros detalles.

![grafana dashboard](https://github.com/jz1k/Kafka-Streaming/blob/main/capturas/grafana.jpg?raw=true)

## Conclusiones

Este proyecto demuestra cómo se puede utilizar Apache Kafka para el procesamiento de streams en tiempo real. Se ha utilizado Spark Streaming para consumir los datos de Kafka y enviarlos a InfluxDB para su almacenamiento y visualización en Grafana. La arquitectura es escalable y se puede adaptar para procesar grandes volúmenes de datos en tiempo real.
