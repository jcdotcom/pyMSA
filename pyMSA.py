from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from threading import Thread
from time import sleep

    #   Function to handle individual MUA client connections

def interactor(connectionSocket, addr):         
    print(f"==========\n  Accepted a new connection {addr}")
    connectionSocket.sendall("220 Welcome to the PyMail MSA Server\r\n".encode())
    connectionSocket.settimeout(10)
    tlds = ["com", "org", "net", "edu", "io", "app"]
    recipients = parts = []
    data = boundary = ""
    response_msg = "250 OK"    # Default response message
    try:
        print(f"   Preparing for transmission...")
        while True:
            text = connectionSocket.recv(1024).decode()
            if("EHLO" in text):
                connectionSocket.sendall("502 OK\r\n".encode())
            elif("HELO" in text):
                connectionSocket.sendall("250 OK\r\n".encode())
            elif("MAIL FROM:" in text):
                sender = text.split(':', 1)[1].strip().strip('<').strip('>')
                connectionSocket.sendall("250 OK\r\n".encode())
            elif("RCPT TO:" in text):
                recipient = text.split(':', 1)[1].strip().strip('<').strip('>')
                recipients.append(recipient)
                if(len(recipients)>5):                                  # Checking for more than 5 recipients
                    response_msg = "550 Too many recipients"
                else:
                    rsplit = recipient.split('@', 1)
                    domain = rsplit[1].split('.')
                    if rsplit[0] == "":                                  # Checking for empty username
                        response_msg = "550 Bad username"
                    elif '@' in rsplit[1]:                               # Checking for too many @'s
                        response_msg = "550 Too many \"@\" symbols"
                    elif domain[0] == "":                              # Checking for empty domain
                        response_msg = "550 Missing domain"
                    elif any(char.isdigit() for char in domain[0]):    # Checking for numbers in domain
                        response_msg = "550 Domain may not contain numbers"
                    elif domain[len(domain)-1] not in tlds:                           # Checking for bad TLD
                        response_msg = "550 Unknown TLD"
                connectionSocket.sendall(f"{response_msg}\r\n".encode())
                if(response_msg != "250 OK"):
                    break
            elif("DATA" in text):
                connectionSocket.sendall("354 OK\r\n".encode())
                print(f"   Receiving data...\n")                        # Receiving Message Body
                while True:
                    try:
                        text = connectionSocket.recv(1024).decode()
                        data += text
                        if text.endswith(".\r\n"):
                            break
                    except UnicodeDecodeError:                          # Handle message exceeding 1024 buffer limit
                        pass
                datas = data.split('\r\n')
                response_msg = "451 Subject cannot be blank"
                for line in datas:
                    if(line.startswith("Subject: ")):
                        response_msg = "250 OK"                                    # Checking for empty subject line
                    if(line.startswith("Content-Type: multipart/mixed;")):          # Checking for attachments in message
                        boundary = line.split("boundary=")[1].replace("-","").replace("\"","")
                        parts = data.split(boundary)[2:-1]
                        if(len(parts)>6):
                            response_msg = "550 Too many attachments"
                            break
                    print(f"{line}")
                connectionSocket.sendall(f"{response_msg}\r\n".encode())
                if response_msg != "250 OK":
                    break
            elif("QUIT" in text):
                    connectionSocket.sendall("221 OK\r\n".encode())
                    break
    except TimeoutError:
        print("   Timeout reached. Closing connection.")  
        print("==========")    
    if response_msg != "250 OK":
        print(f"    ! Error {response_msg} ! ")
    else:
        print(f"    ! Message received successfully ! ")
        if(len(parts)>1):
            print(f"    ! ATTACHMENTS = [ {len(parts)-1} ] ! ")
    connectionSocket.close()
    print(f"  Connection closed with {addr}")
    print("==========\n")    

            # Function to handle incoming connections

def server():       
    # Create a TCP socket that listens to port 9000 on the local host
    welcomeSocket = socket(AF_INET, SOCK_STREAM)
    welcomeSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    welcomeSocket.bind(("", 9000))
    welcomeSocket.listen(4)  # Max backlog 4 connections
    print("\n   Server is listening on port 9000\n")
    try:
        while True:
            connectionSocket, addr = welcomeSocket.accept()
            Thread(target = interactor, args=(connectionSocket,addr)).start()
    except:
        welcomeSocket.close()
        print("   Connection closed")
        print("==========")    

            # Main
def main():
    t1 = Thread(target = server, args=())
    t1.start()

if __name__ == '__main__':
	main()