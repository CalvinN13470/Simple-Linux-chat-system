import socket
import os
import datetime
import signal
import argparse
import selectors
from urllib.parse import urlparse
import sys

#buffer size
BUFFER_SIZE = 2048

#selector variable
sel = selectors.DefaultSelector()

#function when message is received from server
def read(connectionSocket, mask):

    message = connectionSocket.recv(BUFFER_SIZE).decode()

    if message:

        if (message == ("DISCONNECT CHAT/1.0")):
            connectionSocket.close()
            sel.close()
            print("Server has been shutdown")
            sys.exit(0)

        else:
            print(message, end='')

#function when client user enters input
def write(inputStream ,connectionSocket, mask, name):

    if (inputStream):

        sentence = sys.stdin.readline()

        if (sentence.startswith("@" + name + ": ")):
            connectionSocket.send(sentence.encode())
        else:
            print("Please add '@your_name: ' before your message")

def main():

    #signal handling function
    def signal_handler(sig, frame):
        clientSocket.send(("DISCONNECT " + name + " CHAT/1.0").encode())
        print("interruption received")
        clientSocket.close()
        sys.exit(0)

    #signal handler
    signal.signal(signal.SIGINT, signal_handler)

    #check command line arguments

    #parses command arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("name", help="Name to identify client")
    parser.add_argument("url", help="URL detailing name and port number")
    args = parser.parse_args()

    name = args.name
    url = urlparse(args.url)

    if (url.scheme != "chat"):
        print("Incorrect format. Please enter in chat://host_name:portnum format")
        sys.exit(0)


    else:
        #create socket and connect to server
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            clientSocket.connect((url.hostname, url.port))
        
        except socket.gaierror as e:
            print ("Unable to connect to host, please make sure the host name is entered correctly")
            sys.exit(0)

        except ConnectionRefusedError as e:
            print("Connection to host refused, please make sure the socket number is entered correctly")
            sys.exit(0)

    
        #register with server
        clientSocket.send(("REGISTER " + name + " CHAT/1.0").encode())

        #receives code from server
        code = clientSocket.recv(BUFFER_SIZE).decode()

        if (code == "400"):
            print("400 Invalid registration")
            sys.exit()

        elif (code == "401"):
            print("401 Client already registered")
            sys.exit()

        else:
            print("200 Registration successful")

            sel.register(clientSocket, selectors.EVENT_READ, read)
            sel.register(sys.stdin, selectors.EVENT_READ, write)


        #typing input
        while(1):

            events = sel.select(0)
            
            #call appropriate function according to events
            for key, mask in events:
                callback = key.data
                #callback(key.fileobj, mask)

                #write function has different parameters
                if (callback is write):
                    callback(key.fileobj, clientSocket, mask, name)
                else:
                    callback(key.fileobj, mask)
    




if __name__ == '__main__':
    main()