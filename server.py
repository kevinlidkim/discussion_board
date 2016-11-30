#Kevin Li
#109307727
#CSE 310
#Discussion Board Server

#import modules
from socket import *
from threading import *
from SocketServer import *
import select
import sys

user_map = {}

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
        input = [self.server]
        running = 1
        print "Server running"
        while running:
            inputready, outputready, exceptready = select.select(input, [], [])

            for s in inputready:
                if s == self.server:
                    c = Client(self.server.accept())
                    c.start()
                    self.threads.append(c)

                elif s == sys.stdin:
                    junk = sys.stdin.readline()
                    running = 0

        self.server.close()
        for c in self.threads:
            c.join()
                

class Client(Thread):

    def __init__(self, (client, address)):
        Thread.__init__(self)
        self.client = client
        self.address = address
        print "Connection from new client"

    def run(self):
        running = 1
        loggedIn = False
        while running:
            data = self.client.recv(1024)
            if data:

              if loggedIn:
                self.client.send('You are logged in')

              elif (data == "login"):
                self.client.send("Enter user id")
                user_id = self.client.recv(1024)
                if (login(user_id)):
                  self.client.send("Successfully logged in")
                  loggedIn = True
                else:
                  self.client.send("Failed to login")

              else:
                self.client.send(data)

            else:
                self.client.close()
                running = 0


class User(object):
  id = ""

  def __init__(self, id):
    self.id = id
    print "User created with id ", self.id


class Group(object):
  id = ""
  name = ""

  def __init__(self, id, name):
    self.id = id
    self.name = name
    print "Group created with id ", self.id, " and name ", self.name


class Post(object):
  id = ""
  subject = ""
  content = ""

  def __init__(self, id, subject, content):
    self.id = id
    self.subject = subject
    self.content = content


def login(user_id):
  if (user_map.get(user_id) == None):
    user = User(user_id)
    user_map[user_id] = user
    return True
  else:
    print "User already logged in"
    return False


if __name__ == "__main__":
    s = Server()
    s.run()
