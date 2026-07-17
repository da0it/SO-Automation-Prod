import json, hashlib, os, httpx, asyncio, sys 

from httpx_retries import RetryTransport, Retry
from confluent_kafka import Consumer, KafkaException, KafkaError
from app.db.db_handler import handle_call_event_bd, handle_record_added_event_db, update_existing_call_db, SessionDep

kafka_config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'telephony',
    'auto.offset.reset': 'earliest'
}

topics = [
    "mango.events.transcript.ready"
]

class MangoTranscriptWorker():
    def __init__(self):
        self.consumer = Consumer(kafka_config)
        self.handlers = {
            "mango.events.transcript.ready": self.handle_transcript_event
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
    
    def request_transcript(recording_id: str) -> dict:
        api_key = os.getenv("VPBX_API_KEY")
        salt = os.getenv("VPBX_API_SALT")
        url = os.getenv("MANGO_TRANSCRIPTS_URL")

        if not api_key or not salt or not url:
            raise RuntimeError("Mango API variables are not configured")

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
        
        if transcript_result.get("result") == 1000 and transcript_result.get("data"):
            update_existing_call_db(call,
                                    session,
                                    payload=None,
                                    params={"transcript_ready": True},
                    )
            
            ## ПЕРЕДАЧА ДАННЫХ В AI МОДУЛь
            
        else:
            update_existing_call_db(call,
                                    session,
                                    payload=None,
                                    params={"transcript_ready": False},
                )

# Retry Policy
retry = Retry(total=5, total_timeout=30)
transport = RetryTransport(retry=retry)

