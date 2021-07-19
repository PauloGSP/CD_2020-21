"""Example Producer."""

import argparse
import time
import random

import src.middleware
from src.clients import Producer


def _temp():
    """Generate random temperatures."""
    time.sleep(0.1)
    temp = 20
    while True:
        temp += random.randint(-2, 2)
        yield temp


def _msg():
    """Generate random quotes."""

    text = [
        "Ó mar salgado, quanto do teu sal",
        "São lágrimas de Portugal!",
        "Por te cruzarmos, quantas mães choraram,",
        "Quantos filhos em vão rezaram!",
        "Quantas noivas ficaram por casar",
        "Para que fosses nosso, ó mar!",
        "Valeu a pena? Tudo vale a pena",
        "Se a alma não é pequena.",
        "Quem quer passar além do Bojador",
        "Tem que passar além da dor.",
        "Deus ao mar o perigo e o abismo deu,",
        "Mas nele é que espelhou o céu.",
    ]

    time.sleep(0.2)
    yield random.choice(text)


def _weather():
    """Generate weather readings."""
    time.sleep(0.1)
    yield random.randint(0, 40)
    time.sleep(0.1)
    yield random.randint(0, 100)
    time.sleep(0.1)
    yield random.randint(10000, 11000)


def _weather2():
    time.sleep(0.1)
    temp = random.randint(0, 40)
    yield temp
    time.sleep(0.1)
    yield round(temp * 1.8 + 32)
    time.sleep(0.1)
    yield random.randint(0, 100)
    time.sleep(0.1)
    yield random.randint(10000, 11000)


q_protocol = {
    "json": src.middleware.JSONQueue,
    "xml": src.middleware.XMLQueue,
    "pickle": src.middleware.PickleQueue,
}

q_generator = {
    "/temp": _temp,
    "/msg": _msg,
    "/weather": _weather,
    "/weather2": _weather2,
}

q_subtopics = {
    "/temp": "/temp",
    "/msg": "/msg",
    "/weather": ["/weather/temperature", "/weather/humidity", "/weather/pressure"],
    "/weather2": [
        "/weather2/temperature/celsius",
        "/weather2/temperature/fahrenheit",
        "/weather2/humidity",
        "/weather2/pressure",
    ],
}


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--topic",
        help="base topic of producer",
        choices=list(q_generator.keys()),
        default=list(q_generator.keys())[0],
    )
    parser.add_argument("--length", help="number of messages to be sent", default=10)
    parser.add_argument(
        "--queue_type",
        nargs="+",
        help="producers queue type",
        choices=list(q_protocol.keys()),
        default=list(q_protocol.keys())[0],
    )
    args = parser.parse_args()

    p = Producer(
        q_subtopics[args.topic], q_generator[args.topic], q_protocol[args.queue_type]
    )

    p.run(int(args.length))
