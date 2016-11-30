#Kevin Li
#109307727
#CSE 310
#Discussion Board Server

#import modules
from socket import *
from threading import *
from SocketServer import *
from select import *
from sys import *

class Server:

    def __init__(self):
        self.port = 7727
        self.threads = []
        self.server = None
        self.host = ""

    def open_socket(self):
        try:
            self.server = socket(AF_INET, SOCK_STREAM)
            self.server.bind((self.host, self.port))
            self.server.listen(5)
        except socket.error, (value, message):
            if self.server:
                self.server.close()
            print "Could not open socket: " + message
            sys.exit(1)

    def run(self):
        self.open_socket()
        input = [self.server, sys.stdin]
        running = 1
        while running:
            inputready, outputready, exceptready = select(input, [], [])

            for s in inputready:
                if s == self.server:
                    c = ClientThread(self.server.accept())
                    c.start()
                    self.threads.append(c)

                elif s == sys.stdin:
                    junk = sys.stdin.readline()
                    running = 0

        self.server.close()
        for c in self.threads:
            c.join()
                

class ClientThread(Thread):

    def __init__(self, (ip, port)):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        print ("[+] New server socket thread started for " + ip + ":" + str(port))

    def run(self):
        running = 1
        while running:
            data = self.client.recv(1024)
            if data:
                self.client.send(data)
            else:
                self.client.close()
                running = 0

if __name__ == "__main__":
    s = Server()
    s.run()
