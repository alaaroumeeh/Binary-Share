
import socket
import os
import logging
import threading
from time import sleep
from tkinter.filedialog import askopenfilenames


def unit(size):
    if size >= 1024*1024*1024:
        msg = f"{size/(1024*1024*1024):.2f} GB"
    elif size >= 1024*1024:
        msg = f"{size/(1024*1024):.2f} MB"
    elif size >= 1024:
        msg = f"{size/1024:.2f} KB"
    else:
        msg = f"{size} Bytes"
    return msg


def sender():
    try:
        i = 1
        while True:
            filenames = askopenfilenames(title="Client send files")
            if not filenames:
                print("Sender terminated.")
                logging.debug("Sender terminated.")
                break
            msg = f"Send Task#{i}: "
            for filename in filenames: msg += filename + "-"
            logging.debug(msg)   
            for filename in filenames:
                filebasename = os.path.basename(filename)
                size = os.path.getsize(filename)
                namesize = f"{filebasename}|{size}"
                c1.sendall(namesize.encode())
                with open(filename,"rb") as f:
                    filebytes = f.read()
                    total_sent = 0
                    while total_sent < size:
                        sent = c1.send(filebytes[total_sent:])
                        if sent == 0:
                            raise ConnectionError
                        total_sent += sent
                print(f"Sent '{filebasename}' {unit(size)} to {IP}.")
                logging.debug(f"Sent '{filebasename}' {unit(size)} to {IP}.")
                sleep(5)
            i += 1

    except ConnectionError:
        print("Connection Error.")
        logging.error("Connection Error in Sender block.")
    except TimeoutError:
        print("Connection timed out.")
        logging.error("Connection timed out in Sender block.")

    c1.close()
    print(f"Stream C1 closed. {myaddr} -x {IP}")
    logging.debug(f"Stream C1 closed. {myaddr} -x {IP}")

def receiver():
    try:
        i = 1
        while True:
            namesize = c2.recv(128).decode()
            if not namesize:
                print("Receiver terminated.")
                logging.debug("Receiver terminated.")
                break
            NS = namesize.split("|")
            filename = NS[0]
            size = int(NS[1])
            with open(filename,"ab") as f:
                total_recd = 0
                while total_recd < size:
                    chunk = c2.recv(4096)
                    f.write(chunk)
                    total_recd += len(chunk)
            print(f"Received '{filename}' {unit(size)} from {IP}.")
            logging.info(f"Received '{filename}' {unit(size)} from {IP}.")
            i += 1

    except ConnectionError:
        print("Connection Error.")
        logging.error("Connection Error in Receiver block.")
    except TimeoutError:
        print("Connection timed out.") 
        logging.error("Connection timed out in Receiver block.")         

    c2.close()
    print(f"Stream C2 closed. {myaddr} -x {IP}")
    logging.debug(f"Stream C2 closed. {myaddr} -x {IP}")

logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG,filename="client.log")

c1 = socket.socket()
c2 = socket.socket()
myhostname = socket.gethostname()
myaddr = socket.gethostbyname(myhostname) #checkpoint: may return unexpected address.
print(f"myhostname = {myhostname}")
print(f"myaddr = {myaddr}")

while True:
    try:
        IP = input("Enter server IP address:")
        c1.connect((IP,2024))
        print(f"Stream C1 connected: {myaddr} -> {IP}")
        logging.info(f"Stream C1 connected: {myaddr} -> {IP}")
        c2.connect((IP,2024))
        print(f"Stream C2 connected: {myaddr} -> {IP}")
        logging.info(f"Stream C2 connected: {myaddr} -> {IP}")
        break
    except ConnectionError:
        print("Connection Error.")
        logging.error(f"Connection Error in server IP address input block. Server IP={IP}")
    except TimeoutError:
        print("Connection timed out.")
        logging.error("Connection timed out in server IP address input block. Server IP={IP}")

Tsend = threading.Thread(target=sender)
Trecv = threading.Thread(target=receiver)

Tsend.start()
Trecv.start()
print("Sender started.\nReceiver Started.")


