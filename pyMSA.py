from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from threading import Thread
from time import sleep

    #   Function to handle individual MUA client connections

def interactor(connectionSocket, addr):             
    print(f"\nAccepted a new connection {addr}\n")
    connectionSocket.sendall("220 Welcome to the PyMail MSA Server\r\n".encode())
    connectionSocket.settimeout(10)
    tlds = ["com", "org", "net", "edu", "io", "app"]
    recipients = []
    data = ""
    response_msg = "250 OK"    # Default response message
    try:
        while True:
            text = connectionSocket.recv(1024).decode()
            print(f"   {text}")
            if("EHLO" in text):
                connectionSocket.sendall("502 OK\r\n".encode())
            elif("HELO" in text):
                connectionSocket.sendall("250 OK\r\n".encode())
            elif("MAIL FROM:" in text):
                sender = text.split(':', 1)[1].strip().strip('<').strip('>')
                connectionSocket.sendall("250 OK\r\n".encode())
            elif("RCPT TO:" in text):
                recipients.append(text.split(':', 1)[1].strip().strip('<').strip('>'))
                if(len(recipients)>5):                                  # Checking for more than 5 recipients
                    response_msg = "550 Too many recipients"
                else:
                    for r in recipients:
                        user = r.split('@', 1)[0].strip('<')
                        dest = r.split('@', 1)[1].strip('>')
                        domain = dest.split('.')[0]
                        tld = dest.split('.')[1]
                        if user == "":                                  # Checking for empty username
                            response_msg = "550 Bad username"
                        elif '@' in dest:                               # Checking for too many @'s
                            response_msg = "550 Too many \"@\" symbols"
                        elif domain == "":                              # Checking for empty domain
                            response_msg = "550 Missing domain"
                        elif tld not in tlds:                           # Checking for bad TLD
                            response_msg = "550 Unknown TLD"
                connectionSocket.sendall(f"{response_msg}\r\n".encode())
                if(response_msg != "250 OK"):
                    break
            elif("DATA" in text):
                connectionSocket.sendall("354 OK\r\n".encode())
                while True:
                    try:
                        text = connectionSocket.recv(1024).decode()
                        print(f"{text}")
                        data += text
                        if text.endswith(".\r\n"):
                            break
                    except UnicodeDecodeError:
                        pass
                has_subject = False
                datas = data.split('\r\n')
                for line in datas:
                    if(line.startswith("Subject: ")):
                        has_subject = True
                if not has_subject:                                     # Checking for empty subject line
                    response_msg = "451 Subject cannot be empty"
                connectionSocket.sendall(f"{response_msg}\r\n".encode())
            elif("QUIT" in text):
                    connectionSocket.sendall("221 OK\r\n".encode())
                    break
    except TimeoutError:
        print("Timeout reached. Closing connection.")
    if response_msg != "250 OK":
        print(f"Error {response_msg}")
    connectionSocket.close()
    print(f"Connection closed with {addr}")


    # Function to handle incoming connections

def server():       
    # Create a TCP socket that listens to port 9000 on the local host
    welcomeSocket = socket(AF_INET, SOCK_STREAM)
    welcomeSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    welcomeSocket.bind(("", 9000))
    welcomeSocket.listen(4)  # Max backlog 4 connections
    print("Server is listening on port 9000")
    
    try:
        while True:
            connectionSocket, addr = welcomeSocket.accept()
            Thread(target = interactor, args=(connectionSocket,addr)).start()
    except:
        welcomeSocket.close()
        print("Connection closed")


    # Main

def main():
    t1 = Thread(target = server, args=())
    t1.start()

if __name__ == '__main__':
	main()