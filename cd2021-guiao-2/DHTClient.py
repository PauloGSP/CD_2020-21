import socket
import pickle
import logging


class DHTClient:
    def __init__(self, address):
        """ Initialize client."""
        self.dht_addr = address
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.logger = logging.getLogger("DHTClient")

    def put(self, key, value):
        """ Store value to key in the DHT."""
        msg = {"method": "PUT", "args": {"key": key, "value": value}}
        pickled_msg = pickle.dumps(msg)
        self.socket.sendto(pickled_msg, self.dht_addr)
        pickled_msg, addr = self.socket.recvfrom(1024)
        out = pickle.loads(pickled_msg)
        if out["method"] != "ACK":
            self.logger.error("Invalid msg: %s", out)
            return False
        return True

    def get(self, key):
        """ Retrieve key from DHT."""
        msg = {"method": "GET", "args": {"key": key}}
        pickled_msg = pickle.dumps(msg)
        self.socket.sendto(pickled_msg, self.dht_addr)
        pickled_msg, addr = self.socket.recvfrom(1024)
        out = pickle.loads(pickled_msg)
        if out["method"] != "ACK":
            self.logger.error("Invalid msg: %s", out)
            return None
        return out["args"]


if __name__ == "__main__":
    client = DHTClient(("localhost", 5000))
    # add object to DHT (this key is in first node -> local search)
    client.put("1", [0, 1, 2])
    # retrieve from DHT (this key is in first node -> local search)
    print(client.get("1"))

    # add object to DHT (this key is not on the first node -> remote search)
    client.put("2", ("xpto"))
    # retrieve from DHT (this key is not on the first node -> remote search)
    print(client.get("2"))