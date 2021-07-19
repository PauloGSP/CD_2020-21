"""CD Chat server program."""
import logging
import socket
import selectors
from .protocol import CDProto, CDProtoBadFormat, RegisterMessage
logging.basicConfig(filename="server.log", level=logging.DEBUG)


class Server:
    """Chat Server process."""
    def __init__(self):
        self.sel =selectors.DefaultSelector()
        self.address= ('localhost', 2700)
        self.serversock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.serversock.bind(self.address)
        print("[SERVER] Server is up and running")
        logging.debug('Starting')
        self.serversock.listen()
        self.sel.register(self.serversock,selectors.EVENT_READ, self.accept)
        self.totals=[]
        self.totalc={}
        self.serverinfo= {} 
        self.serverinfo[None]=[]
        self.serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def loop(self):
        print(f"[SERVER] Listening on {self.address[0]}:{self.address[1]}.")
        while True:
            events = self.sel.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj,mask)
                
        """^Loop indefinetely.^"""
    def accept(self,sock,mask):
            conn, addr = self.serversock.accept()  # Should be ready
            print(f"[SERVER] The client {addr[0]}:{addr[1]} has joined.")
            self.totalc[conn]=[addr,None]
            logging.debug('client joined %s:%s', addr[0], addr[1])
            conn.setblocking(False)
            self.sel.register(conn, selectors.EVENT_READ, self.read)
            self.serverinfo[None].append(conn)


    def read(self,conn,mask):
        message= CDProto.recv_msg(conn)
        
                    
        logging.debug('[S]Received "%s', message)
        channel=None

        if message:
            if message.command=="register":
                print(f'[SERVER] {message.user} has joined the server')
                self.totalc[conn]=[message.user,None]
                self.totals.append(conn)
            elif message.command=="join":
                channel=message.channel
                self.totalc[conn][1]=channel
                if channel not in self.serverinfo:
                    self.serverinfo[channel]= []
                self.serverinfo[channel].append(conn)
              
                print(f'[SERVER] User {self.totalc[conn][0]} joined the channel {self.totalc[conn][1]}')
            elif message.command== "message":
                step=f'\n[{self.totalc[conn][0]}]: {message.message}'
                channel=message.channel
                msg= CDProto.message(step,channel)
                
                print(f'{step}| channel: {self.totalc[conn][1]}')
                print("my channel is" ,channel)
              
                for socket in self.serverinfo[channel]: 
                    CDProto.send_msg(socket,msg)
                    logging.debug('[S]Sent "%s', msg)
        else:
            print(f'[SERVER] User {self.totalc[conn][0]} has left the server')
            logging.debug('[S] Client %s left', self.totalc[conn][0] )
            for channel in self.serverinfo:
                if conn in self.serverinfo[channel]: 
                    self.serverinfo[channel].remove(conn)
                    

            self.sel.unregister(conn)
            self.totals.remove(conn)
            self.totalc.pop(conn)
            conn.close()