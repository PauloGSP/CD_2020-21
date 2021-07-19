"""Tests two clients."""
import pytest
from DHTClient import DHTClient


@pytest.fixture()
def client():
    return DHTClient(("localhost", 5000))


def test_put_local(client):
    """ add object to DHT (this key is in first node -> local search) """
    assert client.put("1", [0, 1, 2])


def test_get_local(client):
    """ retrieve from DHT (this key is in first node -> local search) """
    assert client.get("1") == [0, 1, 2]


def test_put_remote(client):
    """ add object to DHT (this key is not on the first node -> remote search) """
    assert client.put("2", ("xpto"))


def test_get_remote(client):
    """ retrieve from DHT (this key is not on the first node -> remote search) """
    assert client.get("2") == "xpto"