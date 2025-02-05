import os
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from threading import Thread
from time import sleep

def server():
    # Create a TCP socket that listens to port 9000 on the local host
    welcomeSocket = socket(AF_INET, SOCK_STREAM)
    welcomeSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    welcomeSocket.bind(("", 9000))
    welcomeSocket.listen(4)    # Max backlog 4 connections

    print ('Server is listening on port 9000')
    connectionSocket, addr = welcomeSocket.accept()
    print ("Accept a new connection", addr)

    # Read AT MOST 1024 bytes from the socket
    #text = connectionSocket.recv(1024).decode()
    #print (f"Incoming text is {text}")
    #connectionSocket.send(text.upper().encode())
    #connectionSocket.sendall("HELLO FROM MSA".encode())

        #REFUSE CONNECTION
    #connectionSocket.sendall("554 Not now, im not available \r\n".encode())
                             #or do flush

        #ALLOW CONNECTION
    connectionSocket.sendall("220 accepted \r\n".encode())
    # Read AT MOST 1024 bytes from the socket
    text = connectionSocket.recv(10240).decode()
    print (f"Incoming text is {text}")


    connectionSocket.close()


    welcomeSocket.close()
    print("End of server")

    
    #connectionSocket.close()
    #'Hello from MSA'
    #RFC section 4 doc gives examples of interactions
    #server needs to send numeric code 220 (E: 554 to refuse connectin)

def main():
    print(os.getcwd())
    t1 = Thread(target = server, args=())
    t1.start()

if __name__ == '__main__':
	main()