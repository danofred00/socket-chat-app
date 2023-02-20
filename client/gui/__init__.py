#coding: UTF-8

import tkinter as tk
import tkinter.messagebox as msgbox
from typing import Any, Mapping, Literal

from client.core import ClientObserver
from client.core import Client

from client.gui.functions import *
from client.gui.components import *

from deps.requests import *
from deps.utils import *

from constants import *


class ClientGUI(ClientObserver):

    def __init__(self, title :str, host :str, port :int) -> None:
        super().__init__()

        self.window = tk.Tk()
        self.window.wm_title(title)

        self.WINDOW_WIDTH = 1280
        self.WINDOW_HEIGTH = 800
        self._width = None
        self._heigth = None

        # client observer
        self.client = Client(host_url=host, host_port=port)
        self.client.add_observer(self)

    def _connect_signals(self):
        # connect events
        self.connect('receive', self._on_client_receive)

    def _connect_by_ui(self):
        # start the client
        self._connect_signals()

        # create login ui
        self._setup_login_ui(self.window)
        center_window(self.window, self.login.width, self.login.heigth)

        # show the window
        self.window.mainloop()

    def _connect_by_console(self):
        
        # start the client
        self.client.start()

        # request user info
        username = input('[+] Username : ')
        password = input('[+] Password : ')

        self.client.set_username(username)
        self.client.set_password(password)

        # auth the user
        response = self.client.send_auth_request()

        # check if success
        if response.type == RESPONSE_AUTH_FAIL:
            self.client.close("[-] User Authentication Error")
        elif response.type == RESPONSE_ALREADY_ONLINE:
            self.client.close("[-] User already online")
        elif response.type == RESPONSE_AUTH_SUCCESS:

                # show gui
                self.window.mainloop()
                # start client handling
                self.client.handle()
                # get all clients
                self._request_get_clients()

    def start(self, mode : Literal['MODE_UI', 'MODE_CONSOLE'] = MODE_UI) -> None :
        
        if mode == MODE_UI:
            self._connect_by_ui()
        else:
            self._connect_by_console()
        

    def close(self) -> None:
        self.client.close("[+] Close the Window")
        self.window.quit()

    def _setup_login_ui(self, master) -> None:
        
        self.login = ClientLoginUI(master)
        
        # setup the action when the login button is clicked
        self.login.on_loginBtn_clicked = self._on_loginBtn_clicked
        self.login.pack()
    
    def _on_loginBtn_clicked(self, username, password):
        
        # start the client
        self.client.start()

        self.client.set_username(username)
        self.client.set_password(password)
        
        response = self.client.send_auth_request()
        # just for debug
        # print(response)

        # check if success
        if response.type == RESPONSE_AUTH_FAIL:
            self.client.close("[-] User Authentication Error")
            msgbox.showerror("Login Failed", "Authentification Error, please check your credentials")
        elif response.type == RESPONSE_ALREADY_ONLINE:
            self.client.close("[-] User already online")
            msgbox.showerror("Login Failed", f"User {username} is already online! Please logout before trying again")
        elif response.type == RESPONSE_AUTH_SUCCESS:
            success = msgbox.showinfo("Login Success", "You're Logged in")

            if success:
                self.login.destroy()

                # start client handling
                self.client.handle()

                # get all clients
                self._request_get_clients()               

    def _request_get_clients(self):
        self.client._send_get_clients_request()

    def _on_client_receive(self, event, data = None):
        """
            Actions doing when messages are received
        """
        
        if event.type == RESPONSE_GET_ALL_CLIENTS:

            # we decode content
            clients = event.options['content']
            
            # remove info for the current user
            for client in clients:
                if client['username'] == self.client.username:
                    current = client
                    clients.remove(client)
                    break

            # update items list
            # self.main_ui.set_items(clients)
            # show the main ui
            self._show_main_ui(items=clients, user=current)
        
        elif event.type == RESPONSE_CLIENT_CONNECT:

            # get user about
            # user = (username, addr)
            user = event.options['content']
            print('[+] New user connected %s' % user[0])

            # We do action only if the notified user is not the last connected
            if user[0] != self.client.username:
                # We make a new _ClientChatForm for new user
                self.main_ui._lateral_insert(
                    user[0], 
                    callback= lambda: self.main_ui._create_clientChatForm(
                        item={'username':user[0], 'addr':tuple(user[1])}
                    )
                )

        else:
            message = event.options['content']
            sender = event.headers['sender']

            # request a client name
            self.client.request.send(
                self.client.request_factory.make_request(
                    REQUEST_GET_CLIENT_INFO,
                    options={'content':sender}
                )
            )
            # get a response
            response = self.client.request.get()

            # get a username
            username = response.options['content']

            # display a message
            self.main_ui.frames[username].canvas_draw_message(
                title=username,
                message=message,
                bg_color='white'
            )

    def _send_message(self, message, receiver):
        """
            send the given message to a given receiver
                - message : represent to message to send
                - receiver : is the message receiver (host, port)
        """
        
        self.client.request.send(
            self.client.request_factory.make_request(
                REQUEST_SEND_TO_CLIENT,
                headers={'receiver':receiver},
                options={'content':message}
            )
        )
        
    def _show_main_ui(self, items, user):

        # we setup the menu bar
        self._setup_menu_bar()

        # show the new user interface
        self.main_ui = ClientMainUi(
            self.window, 
            items=items, 
            user=user,
            send_message=self.send_message
        )
        
        center_window(self.window, self.main_ui.width, self.main_ui.height)
        self.main_ui.pack()

    def _setup_menu_bar(self):
        
        menu_bar = tk.Menu(self.window)

        # setup file menu
        file_menu = tk.Menu(menu_bar, title="Files", tearoff=0)
        file_menu.add_command(label='Quit', command=self.close)

        # setup help menu
        help_menu = tk.Menu(menu_bar, title="Help")
        help_menu.add_command(label='Help')
        help_menu.add_command(label='About')

        # setup menu bar
        menu_bar.add_cascade(menu=file_menu)
        menu_bar.add_cascade(menu=help_menu)

        menu_bar.pack()