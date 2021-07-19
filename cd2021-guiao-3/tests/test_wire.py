"""Test consumer/producer interaction on the wire"""
import random
import string
from unittest.mock import MagicMock, patch

import pytest

from src.clients import Producer
from src.middleware import JSONQueue, XMLQueue

TOPIC = "".join(random.sample(string.ascii_lowercase, 6))


def gen():
    while True:
        yield random.randint(0, 100)


def test_simple_producer_JSON(broker):

    producer = Producer(TOPIC, gen, JSONQueue)

    with patch("socket.socket.send", MagicMock()) as send:
        producer.run(1)

        data_sent = send.call_args[0][0]

        assert b"{" in data_sent
        assert b"}" in data_sent
        assert data_sent.count(b"{") == data_sent.count(b"}")
        assert TOPIC.encode("utf8") in data_sent

        assert send.call_args


def test_simple_producer_XML(broker):

    producer = Producer(TOPIC, gen, XMLQueue)

    with patch("socket.socket.send", MagicMock()) as send:
        producer.run(1)

        data_sent = send.call_args[0][0]

        assert b"<" in data_sent
        assert b">" in data_sent
        assert data_sent.count(b"<") == data_sent.count(b">")
        assert TOPIC.encode("utf8") in data_sent
