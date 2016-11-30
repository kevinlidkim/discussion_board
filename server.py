#Kevin Li
#109307727
#CSE 310
#Discussion Board Server

#import modules
from socket import *
from threading import *
from SocketServer import *

class ClientThread(Thread):

    def __init__(self, ip, port):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        print ("[+] New server socket thread started for " + ip + ":" + str(port))

    def run(self):
        while True:
            data = conn.recv(2048)
            print "Server received data: ", data
            MESSAGE = raw_input("Multithreaded Python server : Enter reponse from server:")
            if MESSAGE == 'exit':
                break
            conn.send(MESSAGE)

serverPort = 7727
server = socket(AF_INET, SOCK_STREAM)
server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
server.bind(("", serverPort))
threads = []

while True:
    server.listen(4)
    print "Multithreaded Python server : Waiting for connections from clients..."
    (conn, (ip,port)) = server.accept()
    newThread = ClientThread(ip, port)
    newThread.start()
    threads.append(newThread)

for t in threads:
    t.join()
