#Kevin Li
#109307727
#CSE 310
#Discussion Board Server

# Import modules
from socket import *
from threading import *
from SocketServer import *
import select
import sys
import json

user_map = {}
group_map = {}

# Server class
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
                
# Client class
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
              args = data.split( )

              if loggedIn:

                if (args[0] == "ag"):
                  if (args[1].isdigit()):
                    allGroups(self.client, int(args[1]))
                  else:
                    allGroups(self.client, 5)

                elif (args[0] == "logout"):
                  self.client.send("Logging out")
                  self.client.close()
                  running = 0
                  
                else:
                  self.client.send("Command not recgonized")

              elif (args[0] == "login"):

                if (len(args) > 1):
                  user_id = args[1]
                  if (login(user_id)):
                    self.client.send("Successfully logged in")
                    loggedIn = True
                  else:
                    self.client.send("Failed to login")
                else:
                  self.client.send("User ID not specified")

              elif (args[0] == "help"):
                self.client.send("HELP")

              else:
                self.client.send("Command not recognized")

            else:
                self.client.close()
                running = 0

# User class
class User(object):
  id = ""

  def __init__(self, id):
    self.id = id
    print "User created with id ", self.id

# Group class
class Group(object):
  id = ""
  name = ""

  def __init__(self, id, name):
    self.id = id
    self.name = name
    print "Group created with id ", self.id, " and name ", self.name

# Post class
class Post(object):
  id = ""
  subject = ""
  content = ""

  def __init__(self, id, subject, content):
    self.id = id
    self.subject = subject
    self.content = content

# Login method
def login(user_id):
  if (user_map.get(user_id) == None):
    user = User(user_id)
    user_map[user_id] = user
    return True
  else:
    print "User already logged in"
    return False

# Load user data from json on login
def loadUser
  return

# Save user data to json on logout
def saveUser
  return

# Loads json file
def loadGroups():
  with open('groups.json') as json_data:
    groups = json.load(json_data)
    for group in groups:
      group_map[group['id']] = group['name']

# All group command
def allGroups(client, n):

  index = 1
  client.send(printGroups(index, n))

  while True:
    data = client.recv(1024)

    if (data == "q"):
      client.send("Exit ag")
      break

    elif (data == "n"):
      index = index + n
      if (index > len(group_map)):
        client.send("Reached end of list -- Exit ag")
        break
      else:
        client.send(printGroups(index, n))

    elif (data == "s"):
      client.send("need to implement - subscribe to group")

    elif (data == "u"):
      client.send("need to imeplement - unsubscribe from group")

    else:
      client.send("ag sub-command not recognized")

  return

# print group method from index to n
def printGroups(index, n):
  s = ""

  if (len(group_map) < n+index):
    end = len(group_map)+1
  else:
    end = n+index

  for i in range(index, end):
    s+=str(i)
    s+=". ( ) "
    s+=str(group_map[i])
    s+="\n"
  return s


# Main method
if __name__ == "__main__":
  loadGroups()
  s = Server()
  s.run()
