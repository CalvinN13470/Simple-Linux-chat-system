import socket
import os
import datetime
import signal
import sys
import selectors

#buffer size
BUFFER_SIZE = 2048

#selector variable
sel = selectors.DefaultSelector()

#lists to keep track of client names and client socket
nameList = []
socketList = []

#function when a connection is made from one of the clients
def accept(serverSocket, mask):
    connectionSocket, addr = serverSocket.accept()
    print('Accepted connection from client address: (', addr, ')')

    #Registration message received
    Registration = connectionSocket.recv(BUFFER_SIZE).decode()

    #code 400
    if (not (Registration.startswith("REGISTER") and Registration.endswith("CHAT/1.0"))):
        print("Connection rejected: 400")
        connectionSocket.send(("400").encode())

    else:

        #extracts name
        clientName = Registration[9:(len(Registration) - 9)]

        #code 401
        if (clientName in nameList):
            print("Connection rejected: 401")
            connectionSocket.send(("401").encode())
        
        #code 200
        else:

            connectionSocket.send(("200").encode())

            #add client name to list
            print('Connection to client established, waiting to receive messages from user \'' + clientName + '\'')
            nameList.append(clientName)

            #add client connection socket to list
            socketList.append(connectionSocket)

            sel.register(connectionSocket, selectors.EVENT_READ, read)


#function when a message is received from one of the clients
def read(connectionSocket, mask):
    
    #receive message
    message = connectionSocket.recv(BUFFER_SIZE).decode()

    if message:

        print("Message received: " + message)

        #when client disconnects from server
        if (message.startswith("DISCONNECT") and message.endswith("CHAT/1.0")):

            #removes prefix and suffix leaving the just the name
            name = message[11:(len(message) - 9)]

            print(name + " has disconnected from the server")
            
            #Removes information related to disconnected client
            nameList.remove(name)
            socketList.remove(connectionSocket)
            sel.unregister(connectionSocket)
            connectionSocket.close()

        #sending messages to other clients
        else:
            print("sending message...")
            for clientSocket in socketList:
                if (clientSocket is not connectionSocket):
                    clientSocket.send(message.encode()) 


def main():

    #when program is interrupted, close everything
    def signal_handler(sig, frame):
        print('Interrupt received, notifying all active clients and shutting down server')
        for clientSocket in socketList:
            clientSocket.send(("DISCONNECT CHAT/1.0").encode())
            clientSocket.close()
            serverSocket.close()
            sel.close()

        sys.exit(0)
        

    #signal handler
    signal.signal(signal.SIGINT, signal_handler)

    #setup server
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind(('', 0))
    print('Will wait for client connections at port ' + str(serverSocket.getsockname()[1]))
    print('Waiting for incoming client connections ...')
    serverSocket.setblocking(False)
    serverSocket.listen(100)

    #register server socket in selection as a read event
    sel.register(serverSocket, selectors.EVENT_READ, accept)

    while(1):

        #wait for events to occur
        events = sel.select()

        #call appropriate function according to events
        for key, mask in events:
            callback = key.data
            callback(key.fileobj, mask)


if __name__ == '__main__':
    main()