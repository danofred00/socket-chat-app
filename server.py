#!/usr/bin/python3

from deps.dotenv import env
from deps.requests import *

import socket
import threading


from constants import *
from models.user import UserModel
from models.connection import ConnectionModel

class Server():

    def __init__(self, host : str, port : int) -> None:
        super().__init__()

        self._host = host
        self._port = port
        self._socket = None
        self._connection = None
        
        # models
        self.users = None
        self.connections = None
        self.request = None
        self.request_factory = RequestsFactory()

        # init server
        self.init_server()

        # to remove later
        self.show_header_one_time = True


    def start(self) -> None:        
        
        self._socket.listen()
        if self.show_header_one_time:
            print(f"[+] Serveur en ecoute {self._host}:{self._port}")
            self.show_header_one_time = False


    def handle(self) -> None:

        # handle for clients connections    
        self.thread_handle_conn = threading.Thread(target=self.handle_clients_connection)
        self.thread_handle_conn.start()

    
    def handle_clients_connection(self):
        
        self.handle_connections = True
        while self.handle:

            # get connections
            self._connection, addr = self._socket.accept()
            self.request = RequestModel(self._connection)

            print("\n[+] Nouveau client detecter")
            print("[+] En attente d authentification ...")

            # auth client
            self.auth_client(*addr)
            
            # handle for incoming clients messages
            self.thread_handle_msg = threading.Thread(target=self.handle_for_incoming_messages)
            self.thread_handle_msg.start()


    def stop_handle_for_incoming_msg(self):
        self.handle_messages = False

    def handle_for_incoming_messages(self):

        self.handle_messages = True

        while self.handle_messages:
            response = self.request.get()
            if response.type == REQUEST_SEND_TO_CLIENT:
                print(response)
                self.request.send(response, use_receiver=True)
            
            elif response.type == REQUEST_STOP_SERVER:
                self.close("[+] Kill server by user request : " + REQUEST_STOP_SERVER)


    def init_server(self):

        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.bind((self._host, self._port))
            print(f"[+] Serveur demarrer ...")

            # if everything is okay, we can init all models
            self.init_models()

        except OSError:
            self.close(f"""
                \r[-] Port {self._port} is already used on {self._host}
                \r[-] Please close connection and run it again
            """)

    # init all models
    def init_models(self):
        # init user model
        self.users = UserModel()
        # init connection model
        self.connections = ConnectionModel()
        self.request_factory = RequestsFactory()


    def auth_client(self, host, port):
        
        req = self.request.get()
        if req.type == REQUEST_AUTH_CLIENT:

            data = req.options["content"]
            name, password = tuple(data.strip().split(sep='--'))

            if self.users.auth_user(name, password):

                response_type = RESPONSE_AUTH_SUCCESS
                
                # if ok, we can create a connection for this user
                self.connections.create_connection(
                    self.users.get_by_name(name), 
                    host, port
                )

            else:
                response_type = RESPONSE_AUTH_FAIL
            
            self.request.send(self.request_factory.make_request(
                response_type, headers={"receiver" : (host, port)}
            ))


    
    def send_data(self, data, size: int, feedback = False) -> Response | None:
        
        return self.request.send(self.request_factory.make_simple_request(
            options = {"content": data},
            headers = {
                "content-size": size,
            }
        ), feedback=feedback)
    

    def close(self, reason :str = None):

        # show reason
        print(reason)

        if self._connection != None:
            self._connection.close()
        # close socket
        self._socket.close()



HOST = env('CONFIG_HOST')
PORT = int(env('CONFIG_PORT'))

server = Server(HOST, PORT)

server.start()

server.handle()

# server.close()