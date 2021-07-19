import threading
import time

import pytest

from src.broker import Broker


@pytest.fixture(scope="session")
def broker():
    broker = Broker()

    thread = threading.Thread(target=broker.run, daemon=True)
    thread.start()
    time.sleep(1)
    yield broker
    broker.canceled = True
    thread.join(timeout=5)
