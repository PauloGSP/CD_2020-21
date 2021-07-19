"""Prototype broker clients: consumer + producer."""
from src.middleware import PickleQueue, MiddlewareType


class Consumer:
    """Consumer implementation"""

    def __init__(self, topic, queue_type=PickleQueue):
        """Initialize Queue"""
        self.topic = topic              #guarda o topico
        self.queue = queue_type(f"{topic}")  #invoca o Queue do middleware com o topic como arg em string 
        #self.logger = get_logger(f"Consumer {topic}")
        self.received = []              #lista de mensagens recebidas

    def run(self, events=10):
        """Consume at most <events> events."""
        for _ in range(events):
            topic, data = self.queue.pull() #faz pull da informação do queue
            #self.logger.info("%s: %s", topic, data)
            self.received.append(data)      #adiciona a mensagem à lista de mensagens recebidas


class Producer:
    """Producer implementation"""

    def __init__(self, topic, value_generator, queue_type=PickleQueue):
        """Initialize Queue."""
        #self.logger = get_logger(f"Producer {topic}")

        if isinstance(topic, list):         #se tópico é uma lista
            self.queue = [
                queue_type(subtopic, _type=MiddlewareType.PRODUCER)
                for subtopic in topic
            ]
        else:
            self.queue = [queue_type(topic, _type=MiddlewareType.PRODUCER)]
        self.produced = []  #mensagens produzidas pelo producer
        self.gen = value_generator  #valor

    def run(self, events=10):
        """Produce at most <events> events."""
        for _ in range(events):
            for queue, value in zip(self.queue, self.gen()):
                queue.push(value)   #enviar "value" para todos os tópicos/subtópicos no qual é producer
                #self.logger.info("%s: %s", queue.topic, value)

                self.produced.append(value) #adicionar valor à lista de mensagens produzidas
