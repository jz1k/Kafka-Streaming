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
