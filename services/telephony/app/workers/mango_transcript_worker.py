import json, hashlib, os, httpx, asyncio, sys 

from httpx_retries import RetryTransport, Retry
from confluent_kafka import Producer,Consumer, KafkaException, KafkaError
from app.db.db_handler import (handle_call_event_bd, 
                               handle_record_added_event_db, 
                               get_call_by_entry_id,
                               update_existing_call_db, 
                               engine)
from app.db.db_models import TranscriptState

from sqlmodel import Session

kafka_config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'telephony',
    'auto.offset.reset': 'earliest'
}

topics = [
    "mango.events.record.added"
]


# Retry Policy
retry = Retry(total=5, total_timeout=30)
transport = RetryTransport(retry=retry)


class MangoTranscriptWorker():
    def __init__(self):
        self.consumer = Consumer(kafka_config)
        self.producer = Producer(kafka_config)
        self.handlers = {
            "mango.events.record.added": self.handle_transcript_event
        }
    
    def main_loop(self):
        try:
            self.consumer.subscribe(topics)

            while True:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None: continue
                if msg.error(): 
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                            sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                            (msg.topic(), msg.partition(), msg.offset()))
                    elif msg.error():
                        raise KafkaException(msg.error())
                else:
                    with Session(engine) as session:
                        topic = msg.topic()
                        raw_payload = msg.value().decode("utf-8")
                        handler = self.handlers[topic]
                        handler(session, raw_payload)
                        pass
                    
        except KeyboardInterrupt:
            pass
        finally:
            self.consumer.close() 
    
    def handle_transcript_event(self, session, payload: str = None):
        json_payload = json.loads(payload)
        response = self.request_transcript(json_payload["recording_id"])

        if response.get("result") == 1000 and response.get("data"):
            call = get_call_by_entry_id(json_payload['entry_id'],session)
            
            update_existing_call_db(call,
                                    session,
                                    payload=None,
                                    params={"transcript_state": TranscriptState.READY},
                    )
            
        else:
            update_existing_call_db(call,
                                    session,
                                    payload=None,
                                    params={"transcript_state": TranscriptState.PENDING},
                )

        
        self.producer.produce(topic="mango.events.record.added", value=response)

 
    def request_transcript(self, session, recording_id: str) -> dict:
        api_key = os.getenv("VPBX_API_KEY")
        salt = os.getenv("VPBX_API_SALT")
        url = os.getenv("MANGO_TRANSCRIPTS_URL")

        if not api_key or not salt or not url:
            raise RuntimeError("Mango API variables are not configured")
        
        if json.dumps([recording_id]):
            payload = {
                "recording_id": json.dumps([recording_id], ensure_ascii=False)
            }

        raw_json = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        sign = hashlib.sha256(f"{api_key}{raw_json}{salt}".encode("utf-8")).hexdigest()

        with httpx.Client(transport=transport, timeout=20) as client:  
            response=client.post(
                url,
                data={
                    "vpbx_api_key": api_key,
                    "sign": sign,
                    "json": raw_json,
                },
            )

            response.raise_for_status()
            return response.json()