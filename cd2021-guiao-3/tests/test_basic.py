"""Test simple consumer/producer interaction."""
import json
import pickle
import random
import string
import threading
import time
from unittest.mock import MagicMock, patch

import pytest

from src.clients import Consumer, Producer
from src.middleware import JSONQueue, PickleQueue, XMLQueue

TOPIC = "".join(random.sample(string.ascii_lowercase, 6))


def gen():
    while True:
        yield random.randint(0, 100)


@pytest.fixture
def consumer_JSON():
    consumer = Consumer(TOPIC, JSONQueue)

    thread = threading.Thread(target=consumer.run, daemon=True)
    thread.start()
    return consumer


@pytest.fixture
def consumer_Pickle():
    consumer = Consumer(TOPIC, PickleQueue)

    thread = threading.Thread(target=consumer.run, daemon=True)
    thread.start()
    return consumer


@pytest.fixture
def consumer_XML():
    consumer = Consumer(TOPIC, XMLQueue)

    thread = threading.Thread(target=consumer.run, daemon=True)
    thread.start()
    return consumer


@pytest.fixture
def producer_JSON():

    producer = Producer(TOPIC, gen, PickleQueue)

    producer.run(1)
    return producer


def test_simple_producer_consumer(consumer_JSON, broker):

    producer = Producer(TOPIC, gen, JSONQueue)

    with patch("json.dumps", MagicMock(side_effect=json.dumps)) as json_dump:
        with patch("pickle.dumps", MagicMock(side_effect=pickle.dumps)) as pickle_dump:

            producer.run(10)
            assert pickle_dump.call_count == 0
            assert json_dump.call_count >= 10  # at least 10 JSON messages

    time.sleep(0.1)  # wait for messages to propagate through the broker to the clients

    assert consumer_JSON.received == producer.produced

    assert broker.list_topics() == [TOPIC]


def test_multiple_consumers(consumer_JSON, consumer_Pickle, consumer_XML, broker):

    prev = list(consumer_JSON.received)  # consumer gets previously stored element

    producer = Producer(TOPIC, gen, PickleQueue)

    producer.run(9)  # iterate only 9 times, consumer iterates 9 + 1 historic
    time.sleep(0.1)  # wait for messages to propagate through the broker to the clients

    assert consumer_JSON.received == prev + producer.produced
    assert consumer_Pickle.received == consumer_JSON.received
    assert consumer_Pickle.received == [
        int(v) for v in consumer_XML.received
    ]  # XML only transfers strings, so we cast here into int for comparison

    assert broker.list_topics() == [TOPIC]


def test_broker(producer_JSON, broker):
    time.sleep(0.1)  # wait for messages to propagate through the broker to the clients

    assert broker.list_topics() == [TOPIC]

    assert broker.get_topic(TOPIC) == producer_JSON.produced[-1]
