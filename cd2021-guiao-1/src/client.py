"""CD Chat client program"""
import logging
import socket
import fcntl
import os
import sys
import selectors

from .protocol import CDProto, CDProtoBadFormat, TextMessage

logging.basicConfig(filename=f"{sys.argv[0]}.log", level=logging.DEBUG)


class Client:
    """Chat Client process."""

    def __init__(self, name: str = "Foo"):
        """Initializes chat client."""
        self.name= name
        self.clientsock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.sel = selectors.DefaultSelector()
        self.address=('localhost',2700)
        self.CDProto = CDProto()
        self.channel=None

    def connect(self):
        self.clientsock.connect(self.address)
        self.sel.register(self.clientsock, selectors.EVENT_READ, self.read)
        print(f"[{self.name}] Connecting to {self.address[0]}:{self.address[1]}")
        regist= self.CDProto.register(self.name)
        self.CDProto.send_msg(self.clientsock, regist)



    def read(self,clientsock,mask):
        new= self.CDProto.recv_msg(self.clientsock)
        if type(new) is TextMessage:
            print(new.message)
            logging.debug('[C] Received %s', new)
        
        """Connect to chat server and setup stdin flags."""

    def getkbdata(self,stdin,mask):
        inmsg=stdin.read()
        
        if inmsg!='':
            if inmsg[:-1]== "exit":
                self.clientsock.close()
                sys.exit(f'Cya around {self.name}!')
                logging.debug('[C] Client %s left', self.name)
            elif(inmsg[:5]=="/join"):
                if len(inmsg[6:-1]) > 1: 
                    self.channel=inmsg[6:-1]
                    smsg= self.CDProto.join(self.channel)
                    self.CDProto.send_msg(self.clientsock,smsg)
                    logging.debug('[C] Sent "%s', smsg)
                    print(f'{self.name} has joinned the channel {self.channel}')

                else:
                    print("[ERROR] Invalid channel  ")
            else:
                msg= self.CDProto.message(inmsg,self.channel)
                self.CDProto.send_msg(self.clientsock,msg) 
                logging.debug('[C] Sent "%s', msg)



    def loop(self):
        """Loop indefinetely."""
        print(f"[{self.name}] Connected successfully")
        orig_fl = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
        fcntl.fcntl(sys.stdin, fcntl.F_SETFL, orig_fl | os.O_NONBLOCK)
        self.sel.register(sys.stdin, selectors.EVENT_READ, self.getkbdata)
        while True:
            sys.stdout.write("Input here: ")
            sys.stdout.flush()
            for key, mask in self.sel.select():
                callback = key.data
                callback(key.fileobj,mask)
          
