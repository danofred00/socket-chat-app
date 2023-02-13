#!/usr/bin/python3

from deps.dotenv._dotenv import env
import socket
from threading import Thread

def recv(size :int, _flag :int = ...) -> None :
    
    global conn

    data = conn.recv(1024)
    print("[Client]> " + data.decode('UTF-8'))


def send() -> None:
    # datas:bytes, addr : socket._Address = None
    data = bytes(input("Data to Send : ").encode('UTF-8'))
    bytes_send = conn.sendto(data, addr)
    print(f"[+] Bytes sended : {bytes_send}")


HOST = env('CONFIG_HOST')
PORT = int(env('CONFIG_PORT'))

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST,PORT))

# demarrage du serveur
print(f"[+] Serveur demarrer ...")

# mise en ecoute
print(f"[+] Serveur en ecoute {HOST}:{PORT}")
server.listen()

while True:

    conn, addr = server.accept()
    print(f"[+] Nouveau Client connecter")

    # receive auth packets from 
    while True:
        Thread(target=send).start()  
        Thread(target=recv, args=[1024]).start()  

        

    conn.close()


server.close()