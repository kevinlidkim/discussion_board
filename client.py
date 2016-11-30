from socket import *

serverName = 'localhost'
serverPort = 7727
BUFFER_SIZE = 1024
MESSAGE = raw_input("Client: ")
running = 1

client = socket(AF_INET, SOCK_STREAM)
client.connect((serverName, serverPort))

while running:
    client.send(MESSAGE)
    data = client.recv(BUFFER_SIZE)
    print "Server: ", data
    if (data == "Logging out"):
      running = 0
      break
    MESSAGE = raw_input("Client: ")

client.close()
