import sys
import logging
import json

from confluent_kafka import Consumer, KafkaException, KafkaError
from app.db.db_handler import handle_call_event_bd, handle_recording_event_bd

kafka_config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'telephony',
    'auto.offset.reset': 'earliest'
}

topics = ['mango.events.call',
          'mango.events.recording',
          'mango.events.summary',
          'mango.events.record.added',
        ]

class MangoCallWorker():
    def __init__(self):
        self.consumer = Consumer(kafka_config)

        self.handlers = {
            "mango.events.call": self.handle_call_event,
            "mango.events.recording": self.handle_recording_event,
            "mango.events.summary": self.handle_summary_event,
            "mango.events.record.added": self.handle_record_added_event,
        }
    
    def main_loop(self):
        try:
            self.consumer.subscribe(topics)

            while True:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None: continue
                if msg.error: 
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                            sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                            (msg.topic(), msg.partition(), msg.offset()))
                    elif msg.error():
                        raise KafkaException(msg.error())
                else:
                    print(f"Received message: {msg.value().decode('utf-8')}")
                    
        except KeyboardInterrupt:
            pass
        finally:
            self.consumer.close() 
    
    def handle_call_event(self, validated_payload_raw: str):
        payload = json.loads(validated_payload_raw)
        try:
            handle_call_event_bd(payload)
        except Exception:
            raise 


    def handle_recording_event(self, validated_payload_raw: str):
        payload = json.loads(validated_payload_raw)
        try:
            handle_recording_event_bd(payload)
        except Exception:
            raise



    # def handle_summary_event(self, validated_payload_raw: str):

    # def handle_record_added_event(self, validated_payload_raw: str)