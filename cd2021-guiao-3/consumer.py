"""Example Consumer."""
import argparse

from src.clients import Consumer
from producer import q_generator, q_protocol

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

    c = Consumer(args.topic, q_protocol[args.queue_type])

    c.run(int(args.length))
