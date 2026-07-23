import sys,os, hmac,json 
from fastapi import HTTPException
from hashlib import sha256
from sqlmodel import Session

from dotenv import load_dotenv

from confluent_kafka import Consumer, KafkaException, KafkaError

load_dotenv()

kafka_config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'telephony',
    'auto.offset.reset': 'earliest'
}

topics = [## AI TOPICS
        ]


class MangoCallWorker():
    def __init__(self):
        self.consumer = Consumer(kafka_config)

        self.handlers = {
            "event": self.todo
        }
    
    def main_loop(self):
        try:
            self.consumer.subscribe(topics)

            while True:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None: continue
                error = msg.error()
                if error: 
                    if error.code() == KafkaError._PARTITION_EOF:
                            sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                            (msg.topic(), msg.partition(), msg.offset()))
                    elif error:
                        raise KafkaException(error)
                else:
                    with Session(engine) as session:
                        topic = msg.topic()
                        raw_payload = msg.value().decode("utf-8")
                        handler = self.handlers[topic]
                        handler(raw_payload, session)
                        pass
                    
        except KeyboardInterrupt:
            pass
        finally:
            self.consumer.close() 

    # todo: Запись в журнал аудита
    # def handle_call_event(self, validated_payload_raw: str, session: Session) -> None:
    #     payload = json.loads(validated_payload_raw)
    #     handle_call_event_bd(payload, session)

