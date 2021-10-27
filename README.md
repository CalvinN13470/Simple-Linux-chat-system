# Simple-Linux-chat-system
A simple Python chat program in which a server hosts socket connection and communication between multiple clients. Only works in a Linux environment.

To test the program on your own computer, open two linux 3 linux terminals:
  -1 to host the server
  -2 to be clients
  
As long as you have python3 installed, you can execute the server program by entering:

'python3 server.py'

The client program requires 2 parameters:
 -client ID
 -connection URL
 
An example of executing the client program is:

'python3 client.py bob chat://localhost:12345'

Since you are using your own computer to test this program, keep 'localhost' as the host name. When executing the server, the server will give a port number.

To begin chatting enter:

@clientID: your_message

To shut down either the server or client, send and interrupt signal with Ctrl+C
 
