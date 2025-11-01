import requests
import json
import time
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

KAFKA_TOPIC = "wiki-edits"
KAFKA_BOOTSTRAP_SERVER = "localhost:9092"  # Host machine Kafka port
STREAM_URL = 'https://stream.wikimedia.org/v2/stream/recentchange'
USER_AGENT = 'MyDataProject/1.0 (Python-Requests; student-project; your-email@example.com)'
HEADERS = {
    'User-Agent': USER_AGENT,
    'Accept': 'application/json'
}

def create_kafka_producer():
    print("Connecting to Kafka producer...")
    retries = 30
    for i in range(retries):
        try:
            producer = KafkaProducer(
                bootstrap_servers=[KAFKA_BOOTSTRAP_SERVER],
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            print("Connected to Kafka producer.")
            return producer
        except NoBrokersAvailable:
            print(f"Kafka brokers not available. Retrying in 5s... ({i+1}/{retries})")
            time.sleep(5)
    print("Failed to connect to Kafka after multiple retries.")
    return None

def connect_to_stream(producer):
    print(f"Connecting to Wikipedia stream: {STREAM_URL}")
    try:
        with requests.get(STREAM_URL, headers=HEADERS, stream=True, timeout=30) as r:
            r.raise_for_status()
            print("SUCCESS! Connection established. Streaming data to Kafka...")

            for line in r.iter_lines():
                if not line:
                    continue
                try:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        json_data_str = line_str[6:]
                    elif line_str.startswith('{"$schema":'):
                        json_data_str = line_str
                    else:
                        continue

                    event_data = json.loads(json_data_str)

                    if 'server_name' in event_data and 'title' in event_data:
                        payload = {
                            "server_name": event_data.get("server_name"),
                            "title": event_data.get("title"),
                            "bot": event_data.get("bot", False),
                            "user": event_data.get("user"),
                            "timestamp": event_data.get("timestamp")
                        }
                        producer.send(KAFKA_TOPIC, value=payload)
                        print(f"Sent edit for: {payload['title']} (Bot: {payload['bot']})")

                except json.JSONDecodeError:
                    continue
                except KeyError:
                    continue
                except Exception as e:
                    print(f"An error occurred processing a line: {e}")

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Wikipedia stream: {e}")
    except KeyboardInterrupt:
        print("\nStream stopped by user.")

def main():
    producer = create_kafka_producer()
    if producer:
        try:
            connect_to_stream(producer)
        finally:
            print("Closing Kafka producer...")
            producer.close()
            print("Kafka producer closed.")

if __name__ == "__main__":
    main()
