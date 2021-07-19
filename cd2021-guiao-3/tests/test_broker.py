"""Test simple consumer/producer interaction."""
from unittest.mock import MagicMock, patch

import pytest

from src.broker import Serializer


def test_subscriptions(broker):
    fake_subscriber1 = MagicMock()
    fake_subscriber2 = MagicMock()

    broker.subscribe("/t1", fake_subscriber1, Serializer.JSON)
    broker.subscribe("/t2", fake_subscriber1, Serializer.JSON)
    broker.subscribe("/t2", fake_subscriber2, Serializer.PICKLE)

    assert broker.list_subscriptions("/t1") == [(fake_subscriber1, Serializer.JSON)]

    assert len(broker.list_subscriptions("/t2")) == 2
    assert (fake_subscriber1, Serializer.JSON) in broker.list_subscriptions("/t2")
    assert (fake_subscriber2, Serializer.PICKLE) in broker.list_subscriptions("/t2")

    broker.unsubscribe("/t2", fake_subscriber1)
    assert broker.list_subscriptions("/t2") == [(fake_subscriber2, Serializer.PICKLE)]


def test_topics(broker):
    broker.put_topic("/t3", 1000)

    assert broker.get_topic("/t3") == 1000

    assert broker.get_topic("/t4") == None

    broker.put_topic("/t4", "abc")

    assert broker.get_topic("/t4") == "abc"

    assert len(broker.list_topics()) >= 2  # t3, t4 and the topic from basic
    assert "/t3" in broker.list_topics()
    assert "/t4" in broker.list_topics()
