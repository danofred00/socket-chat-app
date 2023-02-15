#!/usr/bin/python3

import sys
from deps.dotenv import env
from deps.requests import *

import socket
from threading import Thread
from typing import Callable, Optional, Collection


class ClientObserver:

    def __init__(self) -> None:
        
        self._avaliables_events = ['receive']
        self._connected_events = {}

    @property
    def avaliables_events(self):
        return self._avaliables_events
    
    @property
    def connected_events(self) :
        return self._connected_events

    def emit(self, event :str, data = None) -> None:
        
        if event in self._avaliables_events:
            
            if event in self._connected_events.keys():
                e = self._connected_events[event]
                func = e['callback']
                kargs = e['args']

                # calling the function
                func(data, *kargs)
            else:
                raise RuntimeError(f"Signal {event} not connected")


    def connect(self, event :str, callback : Callable, args : Collection = None) -> None:
        
        # connect signal
        if event in self._avaliables_events:
            self._connected_events[event] = {
                "callback": callback, 
                "args": args
            }

class ClientObservable:

    def __init__(self) -> None:
        self._observers : list[ClientObserver] = []
    
    @property
    def observers(self) -> list[ClientObserver]:
        return self._observers

    def add_observer(self, observer : ClientObserver):
        self._observers.append(observer)
    
    
    def emit(self, event :str, data = None):
        for observer in self._observers:
            observer.emit(event, data)

    def remove_observer(self, observer :ClientObserver):
        self._observers.remove(observer)
        

class Client(ClientObservable):

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
            elif response.type == RESPONSE_ALREADY_ONLINE:
                self.close("[-] User already online")

            # start handler
            self.handle()
        except ConnectionAbortedError:
            self.close("Connection Aborted Error")

    def handle(self):

        # handle all incoming messages
        self.thread_handle_msg = Thread(target=self.handle_for_incoming_messages)
        self.thread_handle_msg.start()

    # dispatch messages receive
    def dispatch(self, message, receiver: tuple[str, int] = None):

        msg = self.translate(message)

        if msg == "quit":
            self.send_quit_request()

        elif msg == "kill-server":
            self.request.send(self.request_factory.make_kill_server_request("For Maintenance"))
            # self.close("[+] Quit by killing server")
        
        else:

            self.request.send(self.request_factory.make_request(
                REQUEST_SEND_TO_CLIENT,
                headers={"receiver" : receiver},
                options={"content": message}
            ))
    
    def translate(self, message :str):
        return message.strip()

    def stop_handle_for_incoming_msg(self):
        self.handle_messages = False

    def handle_for_incoming_messages(self):

            self.handle_messages = True

            while self.handle_messages:
                try:
                    response = self.request.get()
                    #print(response)
                    self.emit('receive', response)

                    # # manage all getting response by type
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

class ClientConsole(ClientObserver):

    def __init__(self) -> None:
        super().__init__()
        self.client : Client = Client('user1', 'password1')

        # register this observer
        self.client.add_observer(self)

        # connect signals
        self.connect('receive', self.on_client_receive)

    def on_client_receive(self, event):
        print(event)

    def start(self):
        # start the client
        self.client.start()

        # handle for sending msg
        while True:

            msg = input("[Client]> ")
            self.client.dispatch(msg)



HOST = env('CONFIG_HOST')
PORT = int(env('CONFIG_PORT'))

if __name__ == '__main__':

    client = ClientConsole()

    try:
        client.start()
    except KeyboardInterrupt:
        print("[+] Keyboad interupt")
        # sys.exit(-1)