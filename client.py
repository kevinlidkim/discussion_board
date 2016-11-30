from socket import *

serverName = 'localhost'
serverPort = 7727
BUFFER_SIZE = 1024
MESSAGE = raw_input("Client: ")

client = socket(AF_INET, SOCK_STREAM)
client.connect((serverName, serverPort))

while MESSAGE != 'exit':
    client.send(MESSAGE)
    data = client.recv(BUFFER_SIZE)
    MESSAGE = raw_input("Client: ")

client.close()
