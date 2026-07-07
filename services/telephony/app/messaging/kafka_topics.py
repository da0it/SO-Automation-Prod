from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import KafkaException, KafkaError

def create_kafka_topics() -> None:
    admin_client = AdminClient({
        "bootstrap.servers": "localhost:9092"
    })

    TOPICS = [
    "mango.events.call",
    "mango.events.recording",
    "mango.events.summary",
    "mango.events.record.added",
    ]

    PARTITIONS_COUNT = 1
    REPLICATION_FACTOR = 1

    topics = [
        NewTopic(
            topic=topic_name,
            num_partitions=PARTITIONS_COUNT,
            replication_factor=REPLICATION_FACTOR,
        )
        for topic_name in TOPICS
    ]

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