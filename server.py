#!/usr/bin/python3

from deps.dotenv import env
from deps.requests import *

import socket
import threading
from time import sleep

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
        
        try:
            # handle for clients connections    
            self.thread_handle_conn = threading.Thread(target=self.handle_clients_connection)
            self.thread_handle_conn.start()
        except:
            pass
    
    def handle_clients_connection(self):
        
        self.handle_connections = True
        
        while self.handle:

            # get connections
            self._connection, addr = self._socket.accept()

            print("\n[+] Nouveau client detecter")
            print("[+] En attente d authentification ...")

            # auth client
            if self.auth_client(self._connection):
                
                try:

                    # handle for incoming clients messages
                    self.thread_handle_msg = threading.Thread(target=self.handle_for_incoming_messages, args=[self._connection])
                    self.thread_handle_msg.start()
                except:
                    print("[+] Exception")


    def stop_handling_for_clients_connections(self):
        self.handle_connections = False

    def stop_handle_for_incoming_msg(self):
        self.handle_messages = False

    def handle_for_incoming_messages(self, conn :socket.socket):

        self.handle_messages = True

        while self.handle_messages:
            response = self.request.get(use_sock=True, sock=conn)

            # getting sender
            _sender = self.connections.get_connection_by_addr(
                *response.headers["sender"]
            )

            # manage all requests by type
            if response.type == REQUEST_SEND_TO_CLIENT:
                # just for debug
                print(response)
                
                # get receiver informations
                host, port = response.headers["receiver"]
                print(host, port)
                _conn = self.connections.get_connection_by_addr(host, int(port))

                # forward 
                self.request.send(
                    response,
                    sender=response.headers["sender"],
                    use_receiver=True, 
                    sock=_conn.sock, 
                    use_sock=True
                )

            elif response.type == REQUEST_CLIENT_QUIT:
                # send request
                self.request.send(self.request_factory.make_request(
                    RESPONSE_CLOSE_YOURSELF
                    ), use_sock=True, sock=_sender.sock)
                
                sleep(2.0)

                print("[+] removing connection for user")
                self.connections.remove_connection(tuple(response.headers["sender"]))
                #self.close("[+] Close The server by client request")

            
            elif response.type == REQUEST_STOP_SERVER:
                self.close("[+] Kill server by user request : " + REQUEST_STOP_SERVER)

            elif response.type == REQUEST_GET_ALL_CLIENTS:
                
                self.request.send(self.request_factory.make_request(
                    RESPONSE_GET_ALL_CLIENTS,
                    options={'content':self._get_all_clients()}
                ), use_sock=True, sock=conn)
    
    def _get_all_clients(self):
        
        clients = []
        for conn in self.connections.get_all():
            client = {'username': conn.user.username, 'addr':conn.addr}
            clients.append(client)
        
        return clients

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
        self.request = RequestModel(self._socket)

    # write has_connection method
    def has_connection(self, user :str) -> bool:
        return self.connections.exists_user_connection(user)

    def auth_client(self, connection :socket.socket) ->bool:
        
        req = self.request.get(use_sock=True, sock=connection)
        if req.type == REQUEST_AUTH_CLIENT:

            data = req.options["content"]
            name, password = tuple(data.strip().split(sep='--'))

            res = self.users.auth_user(name, password)

            if res:

                if self.has_connection(name):

                    # if user is already online, we can't connect himself again
                    response_type = RESPONSE_ALREADY_ONLINE
                else:
                    response_type = RESPONSE_AUTH_SUCCESS
                    
                    # if ok, we can create a connection for this user
                    self.connections.create_connection(
                        self.users.get_by_name(name), 
                        connection, 
                        *req.headers["sender"]
                    )

            else:
                response_type = RESPONSE_AUTH_FAIL
            
            # send the auth response
            self.request.send(self.request_factory.make_request(
                response_type, headers={"receiver" : req.headers["sender"]}
            ), use_sock=True, sock=connection)

            return res

    
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

        if self.handle_messages:
            self.stop_handle_for_incoming_msg()
        
        if self.handle_connections:
            self.stop_handling_for_clients_connections()

        if self._connection != None:
            self._connection.close()
        # close socket
        self._socket.close()




HOST = env('CONFIG_HOST')
PORT = int(env('CONFIG_PORT'))

# create the server
server = Server(HOST, PORT)

# running the server
server.start()

# start handling for incomning connecions and messages from clients
server.handle()

# server.close()