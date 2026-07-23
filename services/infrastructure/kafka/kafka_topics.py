from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import KafkaException, KafkaError

def create_kafka_topics() -> None:
    admin_client = AdminClient({
        "bootstrap.servers": "localhost:9092"
    })

    EXTERNAL_TOPICS = [

    # Call state changes
    "mango.events.call",

    # Recording state changes
    "mango.events.call.recording",

    # Recording ended
    "mango.events.summary",

    # Recording is ready for download
    "mango.events.record.added",

    # Transcript state
    "telephony.transcript.state.ready",
    "telephony.transcript.state.failed",
    "telephony.transcript.state.pending"
    ]

    PARTITIONS_COUNT = 1
    REPLICATION_FACTOR = 1
    topics = []

    for topic in EXTERNAL_TOPICS:
        topics.append(
            NewTopic(
                topic=topic,
                num_partitions=PARTITIONS_COUNT,
                replication_factor=REPLICATION_FACTOR,
            )
        )
        

    futures = admin_client.create_topics(topics)

    for topic_name, future in futures.items():
        try:
            future.result()
            print(f"Topic created: {topic_name}")

        except KafkaException as error:
            kafka_error = error.args[0]

            if kafka_error.code() == KafkaError.TOPIC_ALREADY_EXISTS:
                print(f"Topic already exists: {topic_name}")
            else:
                raise