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
    'bootstrap.servers': 'localhost:9092,localhost:9093,localhost:9094'
})

print('Kafka Producer has been initiated...')

def receipt(err, msg):
    if err is not None:
        print('Error: {}'.format(err))
    else:
        message = 'Produced message on topic {} with value of {}\n'.format(msg.topic(), msg.value().decode('utf-8'))
        logger.info(message)
        print(message)
        

def main():
    for i in range(100):
        data = {
            'user_id': fake.random_int(min=20000, max=100000),
            'user_name': fake.name(),
            'user_address': fake.street_address() + ' | ' + fake.city() + ' | ' + fake.country_code(),
            'platform': random.choice(['Mobile', 'Laptop', 'Tablet']),
            'browser': random.choice(['Chrome', 'Firefox', 'Safari', 'Edge', 'Opera']),
            'signup_at': str(fake.date_time_this_month())
        }
        m = json.dumps(data)
        p.poll(1)
        p.produce('logs', m.encode('utf-8'), callback=receipt)
        p.flush()
        time.sleep(1)

if __name__ == '__main__':
    main()