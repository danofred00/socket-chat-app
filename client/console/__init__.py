# coding:utf-8

from client.core import ClientObserver
from client.core import Client


class ClientConsole(ClientObserver):

    def __init__(self, username, password) -> None:
        super().__init__()
        self.client : Client = Client(username, password)

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
