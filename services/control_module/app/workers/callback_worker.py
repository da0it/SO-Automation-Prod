import sys,os, hmac,json 
from sqlmodel import Session

from dotenv import load_dotenv

from confluent_kafka import Consumer, KafkaException, KafkaError

from app.db.db_handler import engine


load_dotenv()

kafka_config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'telephony',
    'auto.offset.reset': 'earliest'
}

topics = ["ai.analysis.state"]


class MangoCallWorker():
    def __init__(self):
        self.consumer = Consumer(kafka_config)

        self.handlers = {
            "ai.analysis.state": self.analysis_handler
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
    def ai_analysis_handler(self, raw_payload: str, session: Session) -> None:
        payload = json.loads(raw_payload)
        update_ai_analysis_state_db(payload, session)
