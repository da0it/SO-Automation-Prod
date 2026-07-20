import sys,os, hmac,json 
from fastapi import HTTPException
from hashlib import sha256
from sqlmodel import Session

from dotenv import load_dotenv

from confluent_kafka import Consumer, KafkaException, KafkaError

from app.db.db_handler import handle_call_event_bd, handle_record_added_event_db, handle_summary_event_db, engine


load_dotenv()

kafka_config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'telephony',
    'auto.offset.reset': 'earliest'
}

topics = ['mango.events.call',
          'mango.events.summary',
          'mango.events.record.added',
        ]


class MangoCallWorker():
    def __init__(self):
        self.consumer = Consumer(kafka_config)

        self.handlers = {
            "mango.events.call": self.handle_call_event,
            "mango.events.summary": self.handle_summary_event,
            "mango.events.record.added": self.handle_record_added_event
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
    def handle_call_event(self, validated_payload_raw: str, session: Session) -> None:
        payload = json.loads(validated_payload_raw)
        handle_call_event_bd(payload, session)
           
    def handle_summary_event(self, validated_payload_raw: str, session: Session) -> None:
        payload = json.loads(validated_payload_raw)
        handle_summary_event_db(payload, session)

    def handle_record_added_event(self, validated_payload_raw: str, session: Session) -> None:
        payload = json.loads(validated_payload_raw)
        handle_record_added_event_db(payload, session)
