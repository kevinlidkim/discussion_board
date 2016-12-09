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
import time

user_map = {}
group_map = {}
help_message = "List of Commands:\n\nlogin userId -- logs you in with specified user id\n\nhelp -- prints out help message which lists all supported commands and subcommands\n\nag [n] -- lists all existing groups, n groups at a time\n\ts [n...] -- subscribes user to specified groups\n\tu [n...] -- unsubscribes user from specified groups\n\tn -- goes to next page of groups\n\tq -- exits ag command\n\nsg [n] -- lists all groups user is subscribed to, n groups at a time\n\tu [n...] -- unsubscribes user from specified groups\n\tn -- goes to next page of groups\n\tq -- exits sg command\n\nrg gname [n] -- displays status, time stamp, and subject line of specified group, n posts at a time\n\t[id] -- displays post of specified id\n\t\tn -- displays more lines of post\n\t\tq -- quits displaying post content\n\tr [x-y] -- marks posts x to y as read\n\tn -- goes to the next page of posts\n\tp -- post to the group\n\tq -- exits rg command\n\nlogout -- logs user out\n"



# Server class
class Server:

  def __init__(self):
    self.port = 7727
    self.threads = []
    self.server = None
    self.host = ""

  # Open socket for connection
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

  # Run the server
  def run(self):
    self.open_socket()
    input = [self.server]
    running = 1
    print "Server running"
    while running:
      inputready, outputready, exceptready = select.select(input, [], [])

      # Multiplex and select on input
      for s in inputready:
        if s == self.server:
          c = Client(self.server.accept())
          c.start()
          self.threads.append(c)

        elif s == sys.stdin:
          junk = sys.stdin.readline()
          running = 0

    # Close the server and connections to all clients
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
    currentUser = 0
    userJsonData = ""

    while running:
      # Get input from client
      data = self.client.recv(1024)
      if data:
        args = data.split( )

        if loggedIn:

          # Run AG command
          if (args[0] == "ag"):
            if (len(args) > 1 and args[1].isdigit() and int(args[1]) > 0):
              allGroups(currentUser, self.client, int(args[1]))
            else:
              allGroups(currentUser, self.client, 5)

          # Run SG command
          elif (args[0] == "sg"):
            if (len(args) > 1 and args[1].isdigit() and int(args[1]) > 0):
              subscribedGroup(currentUser, self.client, int(args[1]))
            else:
              subscribedGroup(currentUser, self.client, 5)

          # Run RG command if given groupname
          elif (args[0] == "rg" and len(args) > 1):
            if (len(args) > 2 and args[2].isdigit() and int(args[2]) > 0):
              readGroup(currentUser, self.client, args[1], args[2])
            else:
              readGroup(currentUser, self.client, args[1], 5)


          # Log user out
          elif (args[0] == "logout"):
            self.client.send("Logging out")
            logout(currentUser)
            self.client.close()
            running = 0

          # Prints list of commands supported
          elif (args[0] == "help"):
            self.client.send(help_message)
            
          # Failed to recognize command while logged in
          else:
            self.client.send("Command not recognized")

        # Log user in
        elif (args[0] == "login"):

          # Get the user id being logged in
          if (len(args) > 1):
            user_id = args[1]

            if (login(user_id)):
              self.client.send("Successfully logged in")
              loggedIn = True
              currentUser = user_id
              loadUser(user_id)

            else:
              self.client.send("Failed to login")

          else:
            self.client.send("User ID not specified")

        # Prints list of commands supported
        elif (args[0] == "help"):
          self.client.send(help_message)

        # Failed to recognize command while logged out
        else:
          self.client.send("Command not recognized")

      else:
          self.client.close()
          running = 0



# User class
class User(object):
  id = ""
  subGroup = {}

  def __init__(self, id):
    self.id = id
    print "User created with id ", self.id

  def getSubGroups(self):
    return self.subGroup

  def setSubGroup(self, groups):
    self.subGroup = groups

  def addSubGroup(self, group_id, group):
    self.subGroup[group_id] = group

  def removeSubGroup(self, group_id):
    del self.subGroup[group_id]


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
# Logs user in by adding them to user_map dictionary of users
def login(user_id):
  if (user_map.get(user_id) == None):
    user = User(user_id)
    user_map[user_id] = user
    return True
  else:
    print "User already logged in"
    return False



# Logout method
# Removes user from user_map dictionary and saves user data to json
def logout(user_id):
  saveUser(user_id)
  del user_map[user_id]



# Load user data from json on login
# Creates json file if not found
def loadUser(user_id):
  fname = "user" + user_id + ".json"

  try:
    with open(fname) as json_data:
      data = json.load(json_data)

      # Store the loaded data into user object
      user = user_map[user_id]
      # Check to see for groups subscribed to
      if (data['subGroup']):
        user.setSubGroup(data['subGroup'])

  except IOError:
    print "User data not found... starting from a blank slate"
    with open(fname, "w") as json_data:
      user_obj = {
        'userId': user_id
      }
      json.dump(user_obj, json_data)



# Save user data to json on logout
def saveUser(user_id):
  fname = "user" + user_id + ".json"

  with open(fname, "w") as json_data:
    user = user_map[user_id]
    subGroup = user.getSubGroups()
    user_obj = {
      'userId': user_id,
      'subGroup': subGroup
    }
    json.dump(user_obj, json_data)



# Loads json file for list of all groups
def loadGroups():
  with open('groups.json') as json_data:
    groups = json.load(json_data)
    for group in groups:
      group_map[group['id']] = group['name']



# All group command
def allGroups(user_id, client, n):

  # Prints out all groups initially
  index = 1
  client.send(printGroups(user_id, index, n))

  while True:
    data = client.recv(1024)
    args = data.split( )

    # Exit ag with q sub command
    if (args[0] == "q"):
      client.send("Exit ag")
      break

    # Go to next list of groups
    elif (args[0] == "n"):
      index = index + n
      # Check for out of bounds error
      if (index > len(group_map)):
        client.send("Reached end of list -- Exit ag")
        break
      else:
        client.send(printGroups(user_id, index, n))

    # Subscribe to group
    elif (args[0] == "s"):
      subscribeToGroupString  = "Subscribed to groups "

      # Go through list of arguments to find out all groups user wants to subscribe to
      for i in range(1, len(args)):
        # Make sure we are not out of bounds
        if (int(args[i]) < (index+n)):
          subscribeToGroupString+=str(args[i])
          subscribeToGroupString+=(" ")
          subscribeToGroup(user_id, args[i])

      client.send(subscribeToGroupString)

    # Unsubscribe from group
    elif (args[0] == "u"):
      unsubscribeFromGroupString  = "Unsubscribed from groups "

      # Go through list of arguments to find out all groups user wants to subscribe to
      for i in range(1, len(args)):
        # Make sure we are not out of bounds
        if (int(args[i]) < (index+n)):
          unsubscribeFromGroupString+=str(args[i])
          unsubscribeFromGroupString+=(" ")
          unsubscribeFromGroup(user_id, args[i])

      client.send(unsubscribeFromGroupString)

    # Sub-command not recognized in ag
    else:
      client.send("ag sub-command not recognized")

  return



# subscribed group command
def subscribedGroup(user_id, client, n):

  user = user_map[user_id]
  subGroup = user.getSubGroups() 

  # Convert subGroup to a list so we can use it to print
  subGroupList = list(subGroup.keys())

  # Prints out your subscribed groups initially
  index = 1
  client.send(printSubGroups(subGroupList, index, n))

  while True:
    data = client.recv(1024)
    args = data.split( )

    # Exit sg with q sub command
    if (args[0] == "q"):
      client.send("Exit sg")
      break

    # Go to next list of groups
    elif (args[0] == "n"):
      index = index + n
      # Check for out of bounds error
      if (index > len(subGroupList)):
        client.send("Reached end of list -- Exit sg")
        break
      else:
        client.send(printSubGroups(subGroupList, index, n))

    # Unsubscribe from group
    elif (args[0] == "u"):
      unsubscribeFromGroupString  = "Unsubscribed from groups "

      # Go through list of arguments to find out all groups user wants to subscribe to
      for i in range(1, len(args)):
        # Make sure we are not out of bounds
        if (int(args[i]) < (index+n)):
          unsubscribeFromGroupString+=str(args[i])
          unsubscribeFromGroupString+=(" ")
          unsubscribeFromSubGroup(subGroupList, user_id, args[i])

      client.send(unsubscribeFromGroupString)

    # Sub-command not recognized in sg
    else:
      client.send("sg sub-command not recognized")

  return



# Read group command
def readGroup(user_id, client, group_name, n):

  # Prints out all groups initially
  index = 1
  client.send("display posts of group")
  reading = False

  while True:
    data = client.recv(1024)
    args = data.split( )

    # If in reading mode
    if reading:
      # Go on to next lines
      if (args[0] == "n"):
        client.send("going onto next lines of post")

      elif (args[0] == "q"):
        client.send("quitting display post mode")
        reading = False

      else:
        client.send("rg [id] sub-command not recognized")

    # Not in reading mode
    else:
      # Exit rg with q sub command
      if (args[0] == "q"):
        client.send("Exit rg")
        break

      # Display post
      elif (args[0].isdigit()):
        client.send("entering display post mode")
        reading = True

      # Go to next list of posts
      elif (args[0] == "n"):
        index = index + n
        # Check for out of bounds error
        if (index > len(group_map)):
          client.send("Reached end of list -- Exit rg")
          break
        else:
          client.send("display next page of posts")

      # Mark post as read
      elif (args[0] == "r"):
        client.send("marks a post as read")

      # post to group
      elif (args[0] == "p"):
        client.send("post to group")

      # Sub-command not recognized in rg
      else:
        client.send("rg sub-command not recognized")

  return



# Print group method from index to n
def printGroups(user_id, index, n):
  s = ""
  user = user_map[user_id]
  subGroup = user.getSubGroups()

  if (len(group_map) < n+index):
    end = len(group_map)+1
  else:
    end = n+index

  for i in range(index, end):
    s+=str(i)
    if (str(i) in subGroup):
      s+=". (s) "
    else:
      s+=". ( ) "
    s+=str(group_map[i])
    s+="\n"
  return s



# Subscribe to group method
def subscribeToGroup(user_id, group_id):
  user = user_map[user_id]
  group = group_map[int(group_id)]
  user.addSubGroup(group_id, group)



# Unsubscribe from group method
def unsubscribeFromGroup(user_id, group_id):
  user = user_map[user_id]
  groups = user.getSubGroups()

  # Check to see if user is subscribed to group before unsubscribing
  if (groups[group_id]):
    user.removeSubGroup(group_id)



# Print subscribed group method from index to n
def printSubGroups(subGroup, index, n):
  s = ""

  index = index - 1

  if (len(subGroup) < n+index):
    end = len(subGroup)
  else:
    end = n+index

  for i in range(index, end):
    s+=str(i+1)
    s+=".     "
    s+=str(group_map[int(subGroup[i])])
    s+="\n"
  return s



# Unsubscribe from group method
def unsubscribeFromSubGroup(group, user_id, group_index):
  user = user_map[user_id]
  groups = user.getSubGroups()
  group_id = group[int(group_index) - 1]

  # Check to see if user is subscribed to group before unsubscribing
  if (groups[group_id]):
    user.removeSubGroup(group_id)



# Main method
if __name__ == "__main__":
  loadGroups()
  s = Server()
  s.run()
