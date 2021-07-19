# coding: utf-8

import socket
import selectors
import signal
import logging
import argparse
import time
# configure logger output format
logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',datefmt='%m-%d %H:%M:%S')
logger = logging.getLogger('Load Balancer')


# used to stop the infinity loop
done = False

sel = selectors.DefaultSelector()

policy = None
mapper = None


# implements a graceful shutdown
def graceful_shutdown(signalNumber, frame):  
    logger.debug('Graceful Shutdown...')
    global done
    done = True


# n to 1 policy
class N2One:
    def __init__(self, servers):
        self.servers = servers  

    def select_server(self):
        return self.servers[0]

    def update(self, *arg):
        pass


# round robin policy
class RoundRobin:
    def __init__(self, servers):
        self.servers = servers
        self.currentserver=-1

    def select_server(self):
        self.currentserver=self.currentserver+1
        if (self.currentserver==len(self.servers)):
            self.currentserver=0
        return self.servers[self.currentserver]
    
    def update(self, *arg):
        pass



# least connections policy
class LeastConnections:
    def __init__(self, servers):
        self.servers = servers
        self.number_of_connections = {}
        for server in self.servers:
            self.number_of_connections[server] = 0

    def select_server(self):
        for server in self.servers:
            print("============================")
            print(server)
            print(self.number_of_connections[server])
        return min(self.number_of_connections.items(), key = lambda t: t[1])[0]

    def update(self, *arg):
        upstream_server = arg[0]
        operation = arg[1]
        print("operação:")
        print(operation)
        self.number_of_connections[upstream_server] += operation

# least response time
class LeastResponseTime:
    def __init__(self, servers):
        self.servers = servers
        self.dic={}
        for s in self.servers: #initializes all servers with 0 time
            self.dic[s]=[0,0]
        
      

    def select_server(self):
        print(self.dic)
        MinValue=0
        for key, value in self.dic.items():
            if value[0]==MinValue:
                iamkey=key
        
        return iamkey

    def update(self, *arg):
        #update the time of thekey in dic
        
        conn=arg[0]
        
        for s in self.dic.keys():
            
            if conn.getpeername()[1] ==s[1]:
                connserver=s
        gottaparse=arg[1]
        if gottaparse=="start":
            stime=arg[2]

            self.dic[connserver][1]=stime
        if gottaparse=="end":
            etime=arg[2]
            self.dic[connserver][0]=etime-self.dic[connserver][1]
        
        print("sou dic",self.dic)
       
    


POLICIES = {
    "N2One": N2One,
    "RoundRobin": RoundRobin,
    "LeastConnections": LeastConnections,
    "LeastResponseTime": LeastResponseTime
}

class SocketMapper:
    def __init__(self, policy):
        self.policy = policy
        self.map = {}
        self.server_sockets = {}     

    def add(self, client_sock, upstream_server):
        client_sock.setblocking(False)
        sel.register(client_sock, selectors.EVENT_READ, read)
        upstream_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        upstream_sock.connect(upstream_server)
        upstream_sock.setblocking(False)
        sel.register(upstream_sock, selectors.EVENT_READ, read)
        logger.debug("Proxying to %s %s", *upstream_server)
        self.map[client_sock] =  upstream_sock
        self.server_sockets[upstream_sock] = upstream_server
        self.server_sockets[client_sock] = upstream_server
        if type(self.policy) == LeastConnections:
            self.policy.update(upstream_server,1)

    def delete(self, sock):
        if type(self.policy) == LeastConnections:
            server = self.server_sockets[sock]
            print(server)
            self.policy.update(server,-1)
        sel.unregister(sock)
        sock.close()
        if sock in self.map:
            self.map.pop(sock)

    def get_sock(self, sock):
        for client, upstream in self.map.items():
            if upstream == sock:
                print("pedi cliente." , upstream)
                timestart=time.process_time()
                policy.update(upstream,"end",timestart)

                return client
            if client == sock:
                print("pedi upstra." , client)
                timestart=time.process_time()
                policy.update(upstream,"start",timestart)

                return upstream
        return None
    
    def get_upstream_sock(self, sock):
        return self.map.get(sock)

    def get_all_socks(self):
        """ Flatten all sockets into a list"""
        return list(sum(self.map.items(), ())) 

def accept(sock, mask):
    client, addr = sock.accept()
    logger.debug("Accepted connection %s %s", *addr)
    mapper.add(client, policy.select_server())

def read(conn,mask):
    data = conn.recv(4096)
    mydata=data.decode().split()
    if mydata[0]=='GET':
        hasbeen=mydata[1].strip("/")
        for key in cache.keys():
            if int(hasbeen)==key:
                mapper.get_sock(conn).send(cache[int(hasbeen)])
                break


    if len(data) == 0: # No messages in socket, we can close down the socket
        mapper.delete(conn)
    else:
        mapper.get_sock(conn).send(data)
       

        if mydata[0]=='Content-Type:':
            for i in range(len(mydata)):
                if mydata[i]=='Pi':
                    precision= mydata[i+3]

                    if len(cache.keys())<5:
                        cache[precision]=data
                        history.append(precision)
                    else:
                        oldest=history[0]
                        del cache[oldest]
                        history.pop(0)
                        cache[precision]=data
                        history.append(precision)

                    break
    
def main(addr, servers, policy_class):
    global policy
    global mapper
    global timestart
    timestart=0
    global cache
    cache={}
    global history
    history=[]
    # register handler for interruption 
    # it stops the infinite loop gracefully
    signal.signal(signal.SIGINT, graceful_shutdown)

    policy = policy_class(servers)
    mapper = SocketMapper(policy)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(addr)
    sock.listen()
    sock.setblocking(False)

    sel.register(sock, selectors.EVENT_READ, accept)

    try:
        logger.debug("Listening on %s %s", *addr)
        while not done:
            events = sel.select(timeout=1)
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)
                
    except Exception as err:
        logger.error(err)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Pi HTTP server')
    parser.add_argument('-a', dest='policy', choices=POLICIES)
    parser.add_argument('-p', dest='port', type=int, help='load balancer port', default=8080)
    parser.add_argument('-s', dest='servers', nargs='+', type=int, help='list of servers ports')
    args = parser.parse_args()
    
    servers = [('localhost', p) for p in args.servers]
    
    main(('127.0.0.1', args.port), servers, POLICIES[args.policy])