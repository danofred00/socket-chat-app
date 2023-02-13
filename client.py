#!/usr/bin/python3

import sys
from deps.dotenv import env
from deps.requests import *

import socket
from threading import Thread
from typing import Callable, Optional


class Client:

    def __init__(
        self, 
        username: str, 
        password: str,
        host_url: Optional[str] = None,
        host_port: Optional[int] = None
    ) -> None:
        # main definition of the function
        super().__init__()

        self.username = username
        self.password = password
        self.host_url = host_url if (host_url != None) else env('CONFIG_HOST')
        self.host_port = host_port if (host_port != None) else int(env('CONFIG_PORT'))

        self._connection = None
        self._socket = None
        self.request = None
        self.request_factory = RequestsFactory()

        # define attributes
        

        # calling methods to init work
        self.connect()

        

    def connect(self):
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.connect((self.host_url, self.host_port))
            
            # 
            #self._connection = self._socket
            self.request = RequestModel(self._socket)

        except ConnectionRefusedError:
            self.close(f"Unable to connect to the server {self.host_url} : {self.host_port}")

    def send_data(self, data, size: int, feedback = False) -> Response | None:
        
        return self.request.send(self.request_factory.make_simple_request(
            options = {"content": data},
            headers = {
                "content-size": size,
            }
        ), feedback=feedback)
    
    def send_auth_request(self) -> Response:
        data = f"{self.username}--{self.password}"
        return self.request.send(
            self.request_factory.make_auth_request(options={"content": data}),
            feedback=True
        )
    
    def start(self):

        try:
            # trying to auth client
            response = self.send_auth_request()

            if(response.type == RESPONSE_AUTH_FAIL):
                self.close("[-] User Authentication Error")
            
            # start handler
            self.handle()
        except ConnectionAbortedError:
            self.close("Connection Aborted Error")

    def handle(self):

        # handle all incoming messages
        self.thread_handle_msg = Thread(target=self.handle_for_incoming_messages)
        self.thread_handle_msg.start()

        # start for writting command line
        self.thread_write_cmd = Thread(target=self.start_command_line)
        self.thread_write_cmd.start()

    def stop_command_line(self):
        self.write_in_command_line = False

    # handling for command line
    def start_command_line(self):

        self.write_in_command_line = True
        while self.write_in_command_line:

            data = input("[Client]> ")
            data_lower = data.lower().strip()
            if data_lower == "quit":
                self.send_quit_request()

            elif data_lower == "kill-server":
                self.request.send(self.request_factory.make_kill_server_request("For Maintenance"))
                # self.close("[+] Quit by killing server")
            
            else:
                receiver = input("Receiver: ")

                self.request.send(self.request_factory.make_request(
                    REQUEST_SEND_TO_CLIENT,
                    headers={"receiver" : (receiver.split(' '))},
                    options={"content": data}
                ))


    def stop_handle_for_incoming_msg(self):
        self.handle_messages = False

    def handle_for_incoming_messages(self):

            self.handle_messages = True

            while self.handle_messages:
                try:
                    response = self.request.get()
                    print(response)

                    # manage all getting response by type
                    if response.type == RESPONSE_CLOSE_YOURSELF:
                        self.close("[+] Closing myself response by server")

                except:
                    pass

    def send_quit_request(self):
        self.request.send(self.request_factory.make_request(
            REQUEST_CLIENT_QUIT
        ))

    def close(self, reason: str = None):

        # show the reason
        print(reason)

        try:
            if self.write_in_command_line:
                self.stop_command_line()
            
            if self.handle_messages:
                self.stop_handle_for_incoming_msg()
        except AttributeError:
            print("[-] Attribute error")

        # close the socket
        self._socket.close()
        sys.exit(-1)



HOST = env('CONFIG_HOST')
PORT = int(env('CONFIG_PORT'))


client = Client('user1', 'password1')
client.start()
