from typing import Dict
from confluent_kafka import Producer, TopicCollection

config = {
    'bootstrap.servers': 'localhost:9092',
    'client.id': 'telephony-producer'
}

telephony_producer = Producer(config)

def delivery_report(err, msg):
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

def produce_event(topic: str, value):
    telephony_producer.produce(topic, value, callback=delivery_report)
    telephony_producer.flush()

