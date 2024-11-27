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
            filenames = askopenfilenames(title="Host send files")
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
                c2.sendall(namesize.encode())
                with open(filename,"rb") as f:
                    filebytes = f.read()
                    total_sent = 0
                    while total_sent < size:
                        sent = c2.send(filebytes[total_sent:])
                        if sent == 0:
                            raise ConnectionError
                        total_sent += sent
                print(f"Sent '{filebasename}' {unit(size)} to {addr2[0]}.")
                logging.debug(f"Sent '{filebasename}' {unit(size)} to {addr2[0]}.")
                sleep(5)
            i += 1
    except ConnectionError:
        print("Connection Error.")
        logging.error("Connection Error in Sender block.")
    except TimeoutError:
        print("Connection timed out.")
        logging.error("Connection timed out in Sender block.")
    c2.close()
    print(f"Stream C2 closed. {myaddr} -x {addr2}")
    logging.debug(f"Stream C2 closed. {myaddr} -x {addr2}")
    
def receiver():
    try:
        i = 1
        while True:
            namesize = c1.recv(128).decode()
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
                    chunk = c1.recv(4096)
                    f.write(chunk)
                    total_recd += len(chunk)
            print(f"Received '{filename}' {unit(size)} from {addr1[0]}.")
            logging.info(f"Received '{filename}' {unit(size)} from {addr1[0]}.")
            i += 1

    except ConnectionError:
        print("Connection Error.")
        logging.error("Connection Error in Receiver block.")
    except TimeoutError:
        print("Connection timed out.") 
        logging.error("Connection timed out in Receiver block.")

    c1.close()
    print(f"Stream C1 closed. {myaddr} -x {addr1}")
    logging.debug(f"Stream C1 closed. {myaddr} -x {addr1}")
    
    
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.DEBUG, filename="host.log")


s = socket.socket()
myhostname = socket.gethostname()
myaddr = socket.gethostbyname(myhostname) #checkpoint: may return unexpected address.
print(f"myhostname = {myhostname}")
print(f"myaddr = {myaddr}")

try:
    s.bind(("",2024))
    print(f"Socket bound to all addresses (include {myaddr}).")
    logging.debug(f"Socket bound to all addresses (include {myaddr}).")
except OSError:
    print("Error binding socket.")
    logging.error("Error binding socket.")
    exit()

s.listen(5)
c1,addr1 = s.accept()
print(f"Stream C1 connected. {addr1} -> {myaddr}")
logging.debug(f"Stream C1 connected. {addr1} -> {myaddr}")
c2,addr2 = s.accept()
print(f"Stream C2 connected. {addr2} -> {myaddr}")
logging.debug(f"Stream C2 connected. {addr2} -> {myaddr}")

Tsend = threading.Thread(target=sender)
Trecv = threading.Thread(target=receiver)

Tsend.start()
Trecv.start()
print("Sender started.\nReceiver Started.")





