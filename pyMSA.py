import os
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from threading import Thread
from time import sleep

def parse_email(data):
    lines = data.split('\r\n')
    recipients = []
    body = []
    is_body = False
    has_subject = False
    subject = ""
    for line in lines:
        if line.startswith("Message-ID:"):
            id = line.split(':', 1)[1].strip()
        elif line.startswith("Date:"):
            date = line.split(':', 1)[1].strip()
        elif line.startswith("MIME-Version:"):
            mime = line.split(':', 1)[1].strip()
        elif line.startswith("User-Agent:"):
            ua = line.split(':', 1)[1].strip()
        elif line.startswith("Content-Language:"):
            lang = line.split(':',1)[1].strip()
        elif line.startswith("To:"):
            recipients.append(line.split(':', 1)[1].strip())
        elif line.startswith("From:"):
            sender = line.split(':', 1)[1]
        elif line.startswith("Subject:"):
            has_subject = True
            subject = line.split(':', 1)[1].strip()
        elif line.startswith("Content-Type:"):
            ct = line.split(':', 1)[1].strip()
        elif line.startswith("Content-Transfer-Encoding:"):
            cte = line.split(':',1)[1].strip()
        elif line.strip() == "":
            is_body = True
        elif is_body:
            if line == ".":
                break
            body.append(line)
    return id, date, mime, ua, lang, recipients, sender, subject, ct, cte, '\n'.join(body).strip(), has_subject

def server():
    # Create a TCP socket that listens to port 9000 on the local host
    welcomeSocket = socket(AF_INET, SOCK_STREAM)
    welcomeSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    welcomeSocket.bind(("", 9000))
    welcomeSocket.listen(4)  # Max backlog 4 connections
    print('Server is listening on port 9000')

    while True:
        connectionSocket, addr = welcomeSocket.accept()
        print("Accepted a new connection", addr)

        connectionSocket.sendall("220 Welcome to the PyMail MSA Server\r\n".encode())
        connectionSocket.settimeout(5)

        tlds = ["com", "org", "net", "edu", "io", "app"]
        recipients = []
        #body = []
        #data = ""
        flag = False
        error = False
        error_msg = "250 OK"
        try:
            while not flag:
                text = connectionSocket.recv(1024).decode()
                if("EHLO" in text):
                    connectionSocket.sendall("502 OK\r\n".encode())
                text = connectionSocket.recv(1024).decode()
                if("HELO" in text):
                    connectionSocket.sendall("250 OK\r\n".encode())
                text = connectionSocket.recv(1024).decode()
                if("MAIL FROM:" in text):
                    sender = text.split(':', 1)[1].strip().strip('<').strip('>')
                    connectionSocket.sendall("250 OK\r\n".encode())
                text = connectionSocket.recv(1024).decode()
                if("RCPT TO:" in text):
                    recipients.append(text.split(':', 1)[1].strip().strip('<').strip('>'))
                    if(len(recipients)>5):
                        error_msg = "550 Too many recipients"
                    else:
                        for r in recipients:
                            user = r.split('@', 1)[0].strip('<')
                            dest = r.split('@', 1)[1].strip('>')
                            domain = dest.split('.')[0]
                            tld = dest.split('.')[1]
                            if user == "":
                                error_msg = "550 Bad username"
                            elif '@' in dest:
                                error_msg = "550 Too many \"@\" symbols"
                            elif domain == "":
                                error_msg = "550 Missing domain"
                            elif tld not in tlds:
                                error_msg = "550 Unknown TLD"
                                break
                    if(error_msg == "250 OK"):
                        connectionSocket.sendall(f"250 OK\r\n".encode())
                    else:
                        flag = True
                        error = True
                        connectionSocket.sendall(f"{error_msg}\r\n".encode())
                        break
                text = connectionSocket.recv(1024).decode()
                if("DATA" in text):
                    connectionSocket.sendall("354 OK\r\n".encode())
                    data = ""
                    while not flag:
                        text = connectionSocket.recv(1024).decode()
                        if(text==".\r\n"):
                            flag = True
                            break
                        data += text
                    id, date, mime, ua, lang, to, frm, sub, ct, cte, body, has_subject = parse_email(data)
                    if not has_subject:
                        connectionSocket.sendall("451 Subject cannot be empty\r\n".encode())
                        error = True
                        error_msg = "451 Subject cannot be empty"
                    else:
                        print("  - has subject")
                        connectionSocket.sendall("250 OK\r\n".encode())
                    flag = True
                else:
                    print("else")
                    connectionSocket.sendall("250 OK\r\n".encode())
                    flag = True
                    break
        except TimeoutError:
            print("Timeout reached. Closing connection.")

        if error:
            print(f"Error {error_msg}")
        else:
            print(f"Sender: {sender}")
            print(f"Recipients: {recipients}")
            print(f"To: {to}")
            print(f"Frm: {frm}")
            print(f"ID: {id}")
            print(f"Date: {date}")
            print(f"MIME: {mime}")
            print(f"ua: {ua}")
            print(f"lang: {lang}")
            print(f"CT: {ct}")
            print(f"CTE: {cte}")
            print(f"lang: {lang}")
            print(f"Subject: {sub}")
            print(f"Body: \n{body}\n")

        connectionSocket.sendall("250 OK\r\n".encode())
        connectionSocket.close()
    welcomeSocket.close()
    print("End of server")


def main():
    #print(os.getcwd())
    t1 = Thread(target = server, args=())
    t1.start()

if __name__ == '__main__':
	main()