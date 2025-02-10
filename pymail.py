import os
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from threading import Thread
from time import sleep

def parse_email(data):
    lines = data.split('\r\n')
    recipients = []
    body = []
    is_body = False
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
            sender = line.split(':', 1)[1].strip()
        elif line.startswith("Subject:"):
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
    return id, date, mime, ua, lang, recipients, sender, subject, ct, cte, ''.join(body).strip()


def server():
    # Create a TCP socket that listens to port 9000 on the local host
    welcomeSocket = socket(AF_INET, SOCK_STREAM)
    welcomeSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    welcomeSocket.bind(("", 9000))
    welcomeSocket.listen(4)  # Max backlog 4 connections
    print('Server is listening on port 9000')

    connectionSocket, addr = welcomeSocket.accept()
    print("Accepted a new connection", addr)

    connectionSocket.sendall("220 Welcome to the PyMail SMTP Server\r\n".encode())

    connectionSocket.settimeout(5)

    tlds = ["com", "org", "net", "edu", "io", "app"]
    #sender = ""
    recipients = []
    #subject = ""
    body = []
    #id = ""
    #date = ""
    #to = ""
    #frm = ""
    #sub = ""
    #cte = ""
    #lang = ""
    data = ""
    #isBody = False
    flag = False
    try:
        while not flag:
            text = connectionSocket.recv(1024).decode()
            print(f"{text}")
            if("EHLO" in text):
                connectionSocket.sendall("502 OK\r\n".encode())
            elif("HELO" in text):
                connectionSocket.sendall("250 OK\r\n".encode())
            elif("MAIL FROM:" in text):
                sender = text.split(':', 1)[1].strip()
                connectionSocket.sendall("250 OK\r\n".encode())
            elif("RCPT TO:" in text):
                recipients.append(text.split(':', 1)[1].strip())
                for r in recipients:
                    rec = r.split('@', 1)[1].strip('>')
                    tld = rec.split('.')[1]
                    print(f"rec {rec}")
                    print(f"tld {tld}")
                    if '@' in rec:
                        connectionSocket.sendall("550 Unknown TLD\r\n".encode())
                        flag = True
                        break
                    elif tld not in tlds:
                        connectionSocket.sendall("550 Unknown TLD\r\n".encode())
                        flag = True
                        break
                connectionSocket.sendall("250 OK\r\n".encode())
            elif("DATA" in text):
                connectionSocket.sendall("354 OK\r\n".encode())
                while not flag:
                    text = connectionSocket.recv(1024).decode()
                    print(f"{text} ---end---")
                    if(text==".\r\n"):
                        flag = True
                        connectionSocket.sendall("250 OK\r\n".encode())
                        break
                    data += text
                id, date, mime, ua, lang, to, frm, sub, ct, cte, body = parse_email(data)
                flag = True
            else:
                connectionSocket.sendall("250 OK\r\n".encode())
                flag = True
                break
    except TimeoutError:
        print("Timeout reached. Closing connection.")


    print(f"     END REACHED      ")
    
    print(f"Sender: {sender}")
    print(f"Recipients: {recipients}")

    print(f"\nID: {id}")
    print(f"\nDate: {date}")
    print(f"\nMIME: {mime}")
    print(f"\nua: {ua}")
    print(f"\nlang: {lang}")
    print(f"\nCT: {ct}")
    print(f"\nCTE: {cte}")
    print(f"\nlang: {lang}")

    print(f"\nSubject: {sub}")
    print(f"\nBody: \n{body}\n")

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