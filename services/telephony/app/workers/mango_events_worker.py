from confluent_kafka import Consumer, KafkaException

config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'telephony',
    'auto.offset.reset': 'earliest'
}

call_consumer = Consumer(config)

call_consumer.subscribe(['mango.events.call',
                         'mango.events.recording',
                         'mango.events.summary',
                         'mango.events.record.added',
                         ])

class MangoCallWorker():
    def __init__(self, config=None):
        self.config = config
    