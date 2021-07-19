"""Message Broker"""
import enum
import json
import pickle
from typing import List
import socket
import selectors
import xml.etree.ElementTree as tree


class Serializer(enum.Enum):
    """Possible message serializers."""

    JSON = 0
    XML = 1
    PICKLE = 2


class Broker:
    """Implementation of a PubSub Message Broker."""

    def __init__(self):
        """Initialize broker."""

        self.canceled = False
        self._host = "localhost"
        self._port = 5000
        self.broker = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.broker.bind((self._host,self._port))
        self.sel = selectors.DefaultSelector()
        self.broker.listen()

        self.topic_consumers = {"/": []}            # {topic1 : [(conn1,SerialENUM),(conn2,SerialENUM)], topic2 : [(conn3,serialENUM)] ....} -> stores the subscribers of each topic
        self.topic_message = {"/": []}              # topic : last_topic_message -> stores the last message published on that topic
        self.consumers_info = {}                    # (consumer socket): serialization_type -> stores the serializer of each consumer
        self.producer_topics = []                   # [topic1,topic2...] -> stores all of the topics produced by the producers/publishers

        self.sel.register(self.broker, selectors.EVENT_READ, self.accept)  

    # connection accept and serialization type storage
    def accept(self,broker,mask):                      

        conn, addr = broker.accept()                                        #accept connection
        header = conn.recv(2).decode('utf-8')                               #receives the 2-byte standard serialization message
        header_size = int(header.replace('f',''))                           #replace headers with 'f' to get the header_size of the next message

        serialization_type = str(conn.recv(header_size).decode('utf-8'))    #this received message has the serialization type of the consumer
        if (serialization_type == "JSONQueue"):
            self.consumers_info[conn] = Serializer.JSON
        elif (serialization_type == "XMLQueue"):
            self.consumers_info[conn] = Serializer.XML
        elif (serialization_type == "PickleQueue"):
            self.consumers_info[conn] = Serializer.PICKLE

        self.sel.register(conn, selectors.EVENT_READ, self.handle)  

    # operation handler (according to the message received by the Queue)
    def handle(self,conn,mask):


            serialization_type = self.consumers_info[conn]                      #get serialization type of the consumer
            header = conn.recv(4)                                               #receive the 4-byte standard header

            if header:                                                          
                header = int(header.decode('utf-8').replace('f',''))            #replace possible 'f' letters from header
                data = conn.recv(header)                                        #receive the encoded message
                
                # decode message according to the consumer serialization type
                if (serialization_type == Serializer.JSON):
                    operation, topic, message = self.decodeJSON(data)
                elif (serialization_type == Serializer.XML):
                    operation, topic, message = self.decodeXML(data)
                elif (serialization_type == Serializer.PICKLE):
                    operation, topic, message = self.decodePickle(data)

                # possible operations
                if (operation == "PUBLISH"):
                    self.put_topic(topic,message)
                elif (operation == "LIST_TOPICS"):
                    topic_list = self.list_topics()
                    self.send(conn,"LIST_TOPICS",topic_list)
                elif (operation == "SUBSCRIBE"):
                    self.subscribe(topic,conn,serialization_type)
                elif (operation == "UNSUBSCRIBE"):
                    self.unsubscribe(topic,conn)

            # unsubscribe that consumer from all topics and close connection
            else:
                self.unsubscribe("",conn) 
                self.sel.unregister(conn)
                conn.close()

    # send message to the consumer
    def send(self, conn, operation : str, data, topic = ""):

        # message encoding
        serialization_type = self.consumers_info[conn]
        if (serialization_type == Serializer.JSON):
            encoded_msg = self.encodeJSON(operation,topic,data)
        elif (serialization_type == Serializer.XML):
            encoded_msg = self.encodeXML(operation,topic,data)
        elif (serialization_type == Serializer.PICKLE):
            encoded_msg = self.encodePickle(operation,topic,data)
        
        # send header + message to the consumer (conn)
        header = str(len(encoded_msg))                               
        size_header = len(header)                               
        newheader= 'f'*(4-size_header) + header 
        conn.send(newheader.encode('utf-8'))  
        conn.send(encoded_msg)              


    def list_topics(self) -> List[str]:                                 
        """Returns a list of strings containing all topics."""

        return self.producer_topics


    def get_topic(self, topic):
        """Returns the currently stored value in topic."""              

        if topic in self.topic_message:
            return self.topic_message[topic]
        else:
            return None


    def put_topic(self, topic, value):                                  
        """Store in topic the value."""

        # store the value as the topic last message and add topic to producer_topics if it doesn't exist
        self.topic_message[topic] = value
        if topic not in self.producer_topics:
            self.producer_topics.append(topic)

        # create new consumer topic if it doesn't exist and migrate all consumers who are subscribed to a super topic of 'topic'
        if topic not in self.topic_consumers.keys():
            self.topic_consumers[topic] = []
            for t in self.topic_consumers.keys():
                if (topic.startswith(t)):
                    for consumer in self.list_subscriptions(t):
                        if consumer not in self.list_subscriptions(topic):
                            self.topic_consumers[topic].append(consumer)
        
        # send message to all the topic subscribers
        if topic in self.topic_consumers:
            for consumer in self.list_subscriptions(topic):
                self.send(consumer[0],"MESSAGE",value,topic)
        else:
            self.topic_consumers[topic] = []


    def list_subscriptions(self, topic: str) -> List[socket.socket]:    #DONE 
        """Provide list of subscribers to a given topic."""

        return self.topic_consumers[topic]


    def subscribe(self, topic: str, address: socket.socket, _format: Serializer = None):   #DONE
        """Subscribe to topic by client in address."""

        # get consumer_info and store the information if it's not on self.consumers_info yet
        consumer_info = (address,_format)
        if address not in self.consumers_info:
            self.consumers_info[address] = _format

        
        # create new consumer topic if it doesn't exist and migrate all consumers who are subscribed to a super topic of 'topic'
        if topic not in self.topic_consumers.keys():
            self.topic_consumers[topic] = []
            for t in self.topic_consumers.keys():
                if (topic.startswith(t)):
                    for consumer in self.list_subscriptions(t):
                        if consumer not in self.list_subscriptions(topic):
                            self.topic_consumers[topic].append(consumer)
        self.topic_consumers[topic].append(consumer_info)

        # add connection to each (sub)topic that starts with topic
        for t in self.topic_consumers.keys():
            if (t.startswith(topic) and consumer_info not in self.topic_consumers[t]):        
                self.topic_consumers[t].append(consumer_info)

        # send last topic's message to the new subscriber if it exists
        if topic in self.topic_message:             
            self.send(address,"message",self.get_topic(topic),topic)


    def unsubscribe(self, topic, address):                          
        """Unsubscribe to topic by client in address."""

        # get consumer info
        serialization_type = self.consumers_info[address]           
        consumer_info = (address,serialization_type)

        # if the consumer has unsubscribed one specific topic (also remove the consumer from its subtopics)
        if (topic != ""):                                          
            for t in self.topic_consumers.keys():
                if (t.startswith(topic)):                           
                    self.topic_consumers[t].remove(consumer_info) 
                    
        # consumer has disconnected (remove it from all the existing topics)
        else:                                                       
            for t in self.topic_consumers.keys():
                if (consumer_info in self.topic_consumers[t]):            
                    self.topic_consumers[t].remove(consumer_info)


    # ENCODE / DECODE ---> JSON

    def encodeJSON(self, operation, topic, data):                                
        message = {'operation': operation, 'topic': topic, 'data': data}
        return (json.dumps(message)).encode('utf-8')

    def decodeJSON(self,data):                                                 
        data = data.decode('utf-8')
        data = json.loads(data)
        operation = data['operation']
        topic = data['topic']
        message = data['data']
        return operation, topic, message


    def encodeXML(self,operation, topic, data): 

        root = tree.Element('root')
        tree.SubElement(root,'operation').set("value",operation)
        tree.SubElement(root,'topic').set("value",topic)
        tree.SubElement(root,'data').set("value",str(data))
        return tree.tostring(root)


    def decodeXML(self,data):
        xml_tree = tree.fromstring(data.decode('utf-8'))      
        operation = xml_tree.find('operation').attrib['value']
        topic = xml_tree.find('topic').attrib['value']
        message = xml_tree.find('data').attrib['value']
        return operation,topic,message


    def encodePickle(self,operation, topic, data):
        pickle_dict = {'operation': operation, 'topic': topic, 'data': data}
        return pickle.dumps(pickle_dict)

    def decodePickle(self,data):
        data = pickle.loads(data)
        operation = data['operation']
        topic = data['topic']
        message = data['data']
        return operation, topic, message


    def run(self):
            """Run until canceled."""

            while not self.canceled:
                events = self.sel.select()
                for key, mask in events:
                    callback = key.data
                    callback(key.fileobj, mask)    