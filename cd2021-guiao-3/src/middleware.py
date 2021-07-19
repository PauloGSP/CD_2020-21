"""Middleware to communicate with PubSub Message Broker."""

#from _typeshed import OpenBinaryMode
from collections.abc import Callable
from enum import Enum
import json, pickle , socket
import xml.etree.ElementTree as tree
from typing import Any


class MiddlewareType(Enum):
    """Middleware Type."""

    CONSUMER = 1
    PRODUCER = 2


class Queue:                
    """Representation of Queue interface for both Consumers and Producers."""

    def __init__(self, topic, _type=MiddlewareType.CONSUMER): 
        """Create Queue."""
  
        self.topic = topic                                                      
        self.type = _type                                                      
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(('localhost', 5000))                                  
        
        # get serialization type class name
        serialization_type = self.__class__.__name__  

        # send header + serialization_type to the broker 
        message_size = str(len(serialization_type))                            
        size_header = len(message_size)                                          
        newheader = 'f'*(2-size_header) + message_size                                          
        self.sock.send(newheader.encode('utf-8'))
        self.sock.send(serialization_type.encode('utf-8'))

        # if it's a consumer, subscribe to the topic
        if self.type == MiddlewareType.CONSUMER:         
            self.subscribe(self.topic)


    def push(self, value):                                 
        """Sends data to broker. """

        self.send("PUBLISH", self.topic, value) 


    def pull(self) -> (str, Any):                          
        """Waits for (topic, data) from broker."""

        header = self.sock.recv(4)                              #receive the 4-byte standard header                  
        header = header.decode('utf-8').replace('f','')         #replace possible 'f' letters from header
        data = self.sock.recv(int(header))                      #receive the encoded message
        operation,topic,message = self.unserialize(data)        #decode message according to the class the connection belongs

        # topic listing and message receiving operations
        if (operation == "LIST_TOPICS"):
            print("==== LIST OF TOPICS ====")
            for t in message:
                print(t)

        elif (operation == "MESSAGE"):
            print("[" + topic + "]]] --> " + str(message))

        return topic,message
   

    def list_topics(self, callback: Callable):              
        """Lists all topics available in the broker."""

        self.send("LIST_TOPICS","","")


    def cancel(self,topic):                                 
        """Cancel subscription."""

        self.send("UNSUBSCRIBE",topic,"")
    

    def subscribe(self,topic):                              
        """Subs to a topic"""

        self.send("SUBSCRIBE",topic,"")


    def send(self, operation, topic, data):                 

        # send header + encoded message message to the consumer (conn)
        data = self.serialize(operation,topic,data)             
        header = str(len(data))                                 
        size_header = len(header)                               
        newheader= 'f'*(4-size_header) + header                 
        self.sock.send(newheader.encode('utf-8'))
        self.sock.send(data)


class JSONQueue(Queue):   
    """Queue implementation with JSON based serialization."""

    def __init__ (self,topic, _type=MiddlewareType.CONSUMER):
        super().__init__(topic,_type)                                            

    def serialize(self, operation, topic, data):                                
        message = {'operation': operation, 'topic': topic, 'data': data}
        return (json.dumps(message)).encode('utf-8')

    def unserialize(self,data):                                                 
        data = data.decode('utf-8')
        data = json.loads(data)
        operation = data['operation']
        topic = data['topic']
        message = data['data']
        return operation, topic, message


class XMLQueue(Queue): #gotta study 
    """Queue implementation with XML based serialization."""

    def __init__ (self,topic, _type=MiddlewareType.CONSUMER):
        super().__init__(topic,_type)

    def serialize(self,operation, topic, data): 

        root = tree.Element('root')
        tree.SubElement(root,'operation').set("value",operation)
        tree.SubElement(root,'topic').set("value",topic)
        tree.SubElement(root,'data').set("value",str(data))
        return tree.tostring(root)


    def unserialize(self,data):
        xml_tree = tree.fromstring(data.decode('utf-8'))      
        operation = xml_tree.find('operation').attrib['value']
        topic = xml_tree.find('topic').attrib['value']
        message = xml_tree.find('data').attrib['value']
        return operation,topic,message


class PickleQueue(Queue):  
    """Queue implementation with Pickle based serialization."""
    
    def __init__ (self,topic, _type=MiddlewareType.CONSUMER):
        super().__init__(topic,_type)

    def serialize(self,operation, topic, data):
        pickle_dict = {'operation': operation, 'topic': topic, 'data': data}
        return pickle.dumps(pickle_dict)

    def unserialize(self,data):
        data = pickle.loads(data)
        operation = data['operation']
        topic = data['topic']
        message = data['data']
        return operation, topic, message


