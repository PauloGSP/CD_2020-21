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

root = "/" + "".join(random.sample(string.ascii_lowercase, 6))
leaf1 = root + "/" + "".join(random.sample(string.ascii_lowercase, 6))
leaf2 = root + "/" + "".join(random.sample(string.ascii_lowercase, 6))


def gen():
    while True:
        yield random.randint(0, 100)


@pytest.fixture
def consumer_JSON():
    consumer = Consumer(root, JSONQueue)

    thread = threading.Thread(target=consumer.run, daemon=True)
    thread.start()
    return consumer


@pytest.fixture
def consumer_Pickle():
    consumer = Consumer(leaf1, PickleQueue)

    thread = threading.Thread(target=consumer.run, daemon=True)
    thread.start()
    return consumer


def test_multiple_producers_to_consumer(consumer_JSON, consumer_Pickle, broker):

    producer1 = Producer(leaf1, gen, JSONQueue) #iwjijdw/jdnwuwhd
    producer2 = Producer(leaf2, gen, JSONQueue) #iwjijdw/ajicfjew

    producer1.run(1)
    producer2.run(1)

    time.sleep(0.1)  # wait for messages to propagate through the broker to the clients

    assert producer1.produced[0] in consumer_JSON.received
    assert producer1.produced[0] in consumer_Pickle.received

    assert producer2.produced[0] not in consumer_Pickle.received
    assert producer2.produced[0] in consumer_JSON.received

    assert all([topic in broker.list_topics() for topic in [leaf1, leaf2]])

    assert root not in broker.list_topics()

    producer3 = Producer(root, gen, JSONQueue)

    producer3.run(1)

    time.sleep(0.1)

    assert root in broker.list_topics()

    assert producer3.produced[0] not in consumer_Pickle.received
