#!/usr/bin/python3

from deps.dotenv._dotenv import env
import socket
from threading import Thread

HOST = env('CONFIG_HOST')
PORT = int(env('CONFIG_PORT'))

def recv(size :int, _flag :int = ...) -> None :
    
    global client

    data = client.recv(1024)
    print("\n[Client]> " + data.decode('UTF-8'))


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#client.bind((HOST,PORT))

try:
    client.connect((HOST,PORT))
    print(f"[+] Client connecter")

    while True:

        Thread(target=recv, args=[1024]).start() 
        Thread(target=client.send, args=[bytes(input("Send to server: ").encode("UTF-8"))]).start()

except ConnectionRefusedError:
    print("[-] connection au serveur impossible")

finally:
    client.close()