import threading

import sys
import argparse
import middleware
import random
import time

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


class Producer(threading.Thread):
    def __init__(self, datatype, length, queue_type=middleware.JSONQueue):
        threading.Thread.__init__(self)

        self.length = length
        self.type = datatype
        self.queue = [queue_type(f"/{self.type}", middleware.MiddlewareType.PRODUCER)]
        if datatype == "temp":
            self.gen = self._temp
        elif datatype == "msg":
            self.gen = self._msg
        elif datatype == "weather":
            self.queue = [
                queue_type(
                    f"/{self.type}/temperature", middleware.MiddlewareType.PRODUCER
                ),
                queue_type(
                    f"/{self.type}/humidity", middleware.MiddlewareType.PRODUCER
                ),
                queue_type(
                    f"/{self.type}/pressure", middleware.MiddlewareType.PRODUCER
                ),
            ]
            self.gen = self._weather
        elif datatype == "weather2":
            self.queue = [
                queue_type(
                    f"/{self.type}/aveiro/temperature/Celsius",
                    middleware.MiddlewareType.PRODUCER,
                ),
                queue_type(
                    f"/{self.type}/aveiro/temperature/Fahrenheit",
                    middleware.MiddlewareType.PRODUCER,
                ),
                queue_type(
                    f"/{self.type}/aveiro/humidity", middleware.MiddlewareType.PRODUCER
                ),
                queue_type(
                    f"/{self.type}/aveiro/pressure", middleware.MiddlewareType.PRODUCER
                ),
            ]
            self.gen = self._weather2

    @classmethod
    def datatypes(self):
        return ["temp", "msg", "weather", "weather2"]

    def _temp(self):
        time.sleep(0.1)
        yield random.randint(0, 40)

    def _msg(self):
        time.sleep(0.2)
        yield random.choice(text)

    def _weather(self):
        time.sleep(0.1)
        yield random.randint(0, 40)
        time.sleep(0.1)
        yield random.randint(0, 100)
        time.sleep(0.1)
        yield random.randint(10000, 11000)

    def _weather2(self):
        time.sleep(0.1)
        t = random.randint(0, 40)
        yield t
        time.sleep(0.1)
        yield round(t * 1.8 + 32)
        time.sleep(0.1)
        yield random.randint(0, 100)
        time.sleep(0.1)
        yield random.randint(10000, 11000)

    def run(self):
        print("Producer start")

        with open(f"/tmp/producer_{self.type}", "w") as fp:
            for _ in range(self.length):
                for queue, value in zip(self.queue, self.gen()):
                    queue.push(value)
                    fp.write(f"{queue.topic} - {value}\n")


class Consumer(threading.Thread):
    def __init__(self, datatype, length, queue_type=middleware.JSONQueue):
        threading.Thread.__init__(self)

        self.score = 0
        self.length = length
        self.type = datatype
        self.queue = queue_type(f"/{self.type}", middleware.MiddlewareType.CONSUMER)

    @classmethod
    def datatypes(self):
        return ["temp", "msg", "weather", "weather2"]

    def run(self, length=10):
        out = []

        print("Consumer start")
        for _ in range(self.length):
            topic, data = self.queue.pull()
            out.append(f"{topic} - {data}")
            print(out[-1])
        with open(f"/tmp/producer_{self.type}") as fp:
            sent = iter(out)
            for line in fp:
                recv = next(sent)
                log = line.rstrip()
                if recv not in log:
                    print(f"DIFF: >{recv}< != >{log}<")
                    return
        self.score = 100


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--length", help="number of messages to be sent", default=10)
    parser.add_argument(
        "--p_queue_type",
        nargs="+",
        help="producers conf [temp, msg, weather],[json, xml, pickle]",
        default="",
    )
    parser.add_argument(
        "--c_queue_type",
        nargs="+",
        help="consumers conf [temp, msg, weather],[json, xml, pickle]",
        default="",
    )

    args = parser.parse_args()

    q_protocol = {
        "json": middleware.JSONQueue,
        "xml": middleware.XMLQueue,
        "pickle": middleware.PickleQueue,
    }

    def parse_conf(thread_list, thread_type):
        lista = []
        for conf in thread_list:
            topic, protocol = conf.split(",")
            if topic not in thread_type.datatypes():
                print(f"Error: {topic} not a valid type: {thread_type.datatypes()}")
                sys.exit(1)
            if protocol not in q_protocol:
                print(f"Error: {protocol} not a valid protocol: {q_protocol}")
                sys.exit(1)

            lista.append(thread_type(topic, int(args.length), q_protocol[protocol]))
        return lista

    producers = parse_conf(args.p_queue_type, Producer)
    consumers = parse_conf(args.c_queue_type, Consumer)

    for c in consumers:
        c.start()

    for p in producers:
        p.start()

    for p in producers:
        p.join()

    score = 0
    for c in consumers:
        c.join()
        score += c.score / len(consumers)

    print(f"EVAL, {score}%")
