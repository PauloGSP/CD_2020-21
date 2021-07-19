"""Protocol for chat server - Computação Distribuida Assignment 1."""
import json
from datetime import datetime
from socket import socket


class Message:
    """Message Type."""
    def __init__(self,command):
        self.command= command

    
class JoinMessage(Message):
    """Message to join a chat channel."""
    def __init__(self,command,channel):
        super().__init__(command)
        self.channel = channel
    def __repr__(self):
        return f'{{"command": "join", "channel": "{self.channel}"}}'

class RegisterMessage(Message):
    """Message to register username in the server."""
    def __init__(self,command,user):
        super().__init__(command)
        self.user= user
    def __repr__(self):
        return f'{{"command": "register", "user": "{self.user}"}}'
    
class TextMessage(Message):
    """Message to chat with other clients."""
    def __init__(self,command,message,ts,channel=None):
        super().__init__(command)
        self.message = message
        self.channel = channel
        self.ts =ts
    def __repr__(self):
        if self.channel is not None:
            return f'{{"command": "message", "message": "{self.message}", "channel": "{self.channel}", "ts": {self.ts}}}'
        else:
            return f'{{"command": "message", "message": "{self.message}", "ts": {self.ts}}}'
class CDProto:
    """Computação Distribuida Protocol."""

    @classmethod
    def register(cls, username: str) -> RegisterMessage:
        """Creates a RegisterMessage object."""
        return RegisterMessage("register",username)

    @classmethod
    def join(cls, channel: str) -> JoinMessage:
        """Creates a JoinMessage object."""
        return JoinMessage("join", channel)

    @classmethod
    def message(cls, message: str, channel: str = None, ts = None) -> TextMessage:
        """Creates a TextMessage object."""
        if ts is None:
            ts = int(datetime.now().timestamp())
        return TextMessage("message",message , ts, channel) 

    @classmethod
    def send_msg(cls, connection: socket, msg: Message):
        """Sends through a connection a Message object."""
        if type(msg) is JoinMessage:
           msg_json= json.dumps({"command":"join", "channel":msg.channel}).encode('utf-8')
        elif type(msg) is RegisterMessage:
            msg_json = json.dumps({"command": "register", "user": msg.user}).encode('utf-8')
        elif type(msg) is TextMessage:
            if msg.channel is not None:
                msg_json = json.dumps({"command": "message", "message": msg.message, "channel": msg.channel, "ts": int(datetime.now().timestamp())}).encode('utf-8')
            else:
                msg_json = json.dumps({"command": "message", "message": msg.message, "ts": int(datetime.now().timestamp())}).encode('utf-8')

        head = len(msg_json).to_bytes(2,'big')
        connection.sendall(head+msg_json)
 
    @classmethod
    def recv_msg(cls, connection: socket) -> Message:
        """Receives through a connection a Message object."""

        head= int.from_bytes(connection.recv(2),'big') 
 
        if head == 0:
            return

        message= connection.recv(head).decode('utf-8')
        try:
            decmesg= json.loads(message)
        except json.JSONDecodeError as err:
            raise CDProtoBadFormat(message)
        if decmesg['command'] =="join": 
            channel = decmesg["channel"]
            return CDProto.join(channel)
        elif decmesg['command'] =="register":
            user = decmesg["user"]
            return CDProto.register(user)  
        elif decmesg['command'] =="message":
            
            msg= decmesg["message"]
            channel = decmesg["channel"] if "channel" in decmesg else None
            ts =decmesg["ts"]
            return CDProto.message(msg, channel, ts)



class CDProtoBadFormat(Exception):
    """Exception when source message is not CDProto."""

    def __init__(self, original_msg: bytes=None) :
        """Store original message that triggered exception."""
        self._original = original_msg

    @property
    def original_msg(self) -> str:
        """Retrieve original message as a string."""
        return self._original.decode("utf-8")
