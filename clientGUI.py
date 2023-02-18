#coding: UTF-8

import tkinter as tk
import tkinter.font as font
import tkinter.ttk as ttk
import tkinter.messagebox as msgbox
import tkinter.dialog as dialog
from typing import Any, Mapping

from client import *
from deps.requests import *
from deps.utils import *


def center_window(window :tk.Tk, width:int, heigth:int):
    
    # get the size of the screen
    x = window.winfo_screenwidth()
    y = window.winfo_screenheight()

    # get the center
    x = (x/2) - (width/2)
    y = (y/2) - (heigth/2)

    # center the window
    window.wm_geometry("%dx%d+%d+%d" % (width, heigth, x, y))

class ClientGUI(ClientObserver, tk.Tk):

    def __init__(self) -> None:
        super().__init__()

        self.window = tk.Tk()
        self.WINDOW_WIDTH = 1280
        self.WINDOW_HEIGTH = 800
        self._width = None
        self._heigth = None

        # client observer
        self.client = Client()
        self.client.add_observer(self)
    
    def connect_signals(self):

        # connect events
        self.connect('receive', self.on_client_receive)

    def start(self) -> None :
        
        # start the client
        self.connect_signals()

        # create login ui
        self.create_login_ui(self.window)
        center_window(self.window, self.login.width, self.login.heigth)

        # show the window
        self.window.mainloop()

    def close(self) -> None:
        self.client.close("[+] Close the Window")
        self.window.quit()

    def create_login_ui(self, master) -> None:
        
        self.login = ClientLoginUI(master)
        
        # setup the action when the login button is clicked
        self.login.on_loginBtn_clicked = self.on_loginBtn_clicked
        self.login.pack()
    
    def on_loginBtn_clicked(self, username, password):
        
        # start the client
        self.client.connect()

        self.client.set_username(username)
        self.client.set_password(password)
        
        response = self.client.send_auth_request()
        # just for debug
        print(response)

        # check if success
        if response.type == RESPONSE_AUTH_FAIL:
            self.client.close("[-] User Authentication Error")
            msgbox.showerror("Login Failed", "Authentification Error, please check your credentials")
        elif response.type == RESPONSE_ALREADY_ONLINE:
            self.client.close("[-] User already online")
            msgbox.showerror("Login Failed", f"User {username} is already online! Please logout before trying again")
        elif response.type == RESPONSE_AUTH_SUCCESS:
            print("Success")
            success = msgbox.showinfo("Login Success", "You're Logged in")

            if success:
                self.login.destroy()
                # show the new user interface
                self.main_ui = ClientMainUi(self.window)
                center_window(self.window, self.main_ui.width, self.main_ui.height)
                self.main_ui.pack()

        
    def on_client_receive(self, event):
        print(event)

    
    def show_main_ui(self):
        pass

class ClientLoginUI(tk.Frame):

    def __init__(self, master: tk.Misc | None = ..., width = 500, heigth = 500) -> None:
        super().__init__(master, width=width, height=heigth)
        
        self.width = width
        self.heigth = heigth
        self.on_loginBtn_clicked = None
        self.draw()

    def draw(self) -> None:

        tk.Label(self, font=("Segoe UI", 32, font.BOLD), text="Socket Chat-App").pack()
        tk.Label(self, font=("Segoe UI", 18), text="Enter your login credentials here to start").pack(fill=tk.X)
        
        frame = tk.LabelFrame(self, text="Login", padx=10, pady=10)
        # entry for username
        tk.Label(frame, font=("Segoe UI", 20, font.BOLD), text="Username").grid(column=0, row=0)
        # with and height represent the numbers of chars in the x axis and y axis
        self._username = tk.Text(frame, width=20, height=1, font=("", 20), padx=5, pady=5)
        self._username.grid(column=1, row=0, pady=20)
        # entry for password
        tk.Label(frame, font=("Segoe UI", 20, font.BOLD), text="Password").grid(column=0, row=1)
        self._password = tk.Text(frame, width=20, height=1, font=("", 20), padx=5, pady=5)
        self._password.grid(column=1, row=1, pady=40)
        
        # LOGIN BUTTON
        self._login = tk.Button(frame, text="LOGIN", relief=tk.SOLID, 
                                font=("Segoe UI", 20, font.BOLD), width=10,
                                border=0, bg="#27BCE2", fg="#ffffff",
                                activeforeground="#ffffff", activebackground="#1F92AF",
                                command=lambda: self.on_loginBtn_clicked(self.username, self.password)
                            )
        self._login.grid(row=2, column=0, columnspan=2)
        
        # show the frame
        frame.pack(anchor=tk.CENTER, pady=10)
        tk.Label(self, text="By @Danofred0").pack(fill=tk.X)
    

    @property
    def username(self) -> str:
        return str(self._username.get('1.0', tk.END)).strip()

    @property
    def password(self) -> str:
        return str(self._password.get('1.0', tk.END)).strip()

    @property
    def login_button(self) -> tk.Button:
        return self._login

class ClientMainUi(tk.Frame):

    def __init__(self, master : tk.Widget, width :int = 1200, height :int = 800) -> None:
        super().__init__(master, width=width, height=height)

        self.width = width
        self.height = height

        ##
        self.items = []

        # setup the screen
        self.setup()
        
        # events
        # to do later
    
    def on_lateral_item_selected(self, event):

        selection = self.lateral.item(event.widget.selection())
        title = selection['values'][0]
        self.show_frame(title)
    
    def _setup_lateral_bar(self):
        self.lateral = ttk.Treeview(self.content)
        self.lateral['style'] = 'TreeView'
        self.lateral['columns'] = ('clients')
        self.lateral.configure(height=self.height)
        self.lateral.column('#0', width=0, stretch=tk.NO)
        self.lateral.heading("clients", text="Clients")

        # insert fake datas
        self.items = ['Item1', 'Item2', 'Item3']
        
        for item in self.items:  
            # insert element
            self.lateral.insert('', tk.END, values=(item))
        
        # bind selection event
        self.lateral.bind('<<TreeviewSelect>>', self.on_lateral_item_selected)

        # add to the main content
        self.content.add(self.lateral, width=290)

    def _setup_main_component(self):

        # frame list
        self.frames = {}

        self.main = tk.Frame(self.content)
    
        _f = tk.Frame(self.main)
        self.frames['main'] = _f
        self.default_main(_f).grid(column=0, row=0, sticky='nsew', pady=200, padx=200)
        self.frames['main'].grid(column=0, row=0, sticky='nsew')
        for item in self.items:

            frame = _ClientChatForm(self.main, title=item)
            self.frames[item] = frame
            self.frames[item].grid(column=0, row=0, sticky='nsew')
        
        self.show_frame('Item1')

        # add to the main content
        self.content.add(self.main)
    
    def default_main(self, master) -> tk.Frame:
        frame = tk.Frame(master, background='#302F2F')

        # add something inside here
        tk.Label(frame, font=self.font_title, text='Socket Chat App').pack()
        tk.Label(frame, text='By @Danofred').pack()

        return frame
    
    def show_frame(self, name):
        """
            Display the frame set by name
        """
        frame = self.frames[name]
        frame.tkraise()

    def _setup_style(self):

        style = ttk.Style()
        style.theme_use('default')

        style.configure('TreeView',
            background='white',
            foreground='black',
            rowheight=25,
            fieldbackground='white',
            font=font.Font(size=18)
        )

        style.map('TreeView', background=[('selected', '#17ABEC')])

        style.configure('TreeView.Heading', font=self.font_title, bg="green", border=2)
        style.layout('TreeView', [
            ('app.TreeView.treearea', {'sticky':'nsew', 'border':10})
        ])
    
    def _setup_fonts(self):
        self.font_title = font.Font(family='Comic sans ms', size=48, weight=font.BOLD)

    def setup(self):
        self.content = tk.PanedWindow(self, width=self.width, height=self.height)
        # setup the style
        self._setup_fonts()
        self._setup_style()        
        self._setup_lateral_bar()
        self._setup_main_component()
        self.content.pack(fill=tk.BOTH)


class _ClientChatForm(tk.Frame):

    def __init__(self, master, width = 998, height = 800, title :str = None):
        super().__init__(master)

        self.width = width
        self.height = height
        self.title = title

        # setup the widget
        self.setup()

    def setup(self):
        self._setup_font()
        self._setup_status_bar()
        self._setup_canvas()
        self._setup_form()

    def _setup_status_bar(self):
        frame = tk.Frame(self, bg='#8E8888')
        tk.Label(frame, text=self.title.title(), font=self.font_title).pack(side=tk.LEFT)
        frame.grid(column=0, row=0, sticky='nsew')
    
    def _setup_font(self):

        DEFAULT_FAMILLY = 'comic sans ms'

        self.font_title = font.Font(family=DEFAULT_FAMILLY, size=20, weight=font.BOLD)
        self.font_message_user = font.Font(family=DEFAULT_FAMILLY, size=16, weight=font.BOLD)
        self.font_message_content = font.Font(family=DEFAULT_FAMILLY, size=18, weight=font.NORMAL)

    def _setup_canvas(self):

        frame = tk.Frame(self)
        self.canvas = tk.Canvas(frame, background='#8E8888')
        self.cv_yScrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL)

        # configure it
        self.canvas.configure(height=625, width=885)
        self.cv_yScrollbar.configure(command=self.canvas.yview)

        # setup the default position to start sending message
        self.current_x, self.current_y = 10, 10

        # setup the scrollbar
        self.cv_yScrollbar.pack(side=tk.RIGHT)
        self.canvas.pack(side=tk.LEFT)
        
        frame.grid(column=0, row=1, sticky='nsew')

    def canvas_draw_message(self, title:str, message:str, bg_color = 'green'):

        canvas = self.canvas
        CHAR_WIDTH = 15
        CHAR_HEIGHT = 40
        MESSAGE_MARGIN_BOTTOM = 30

        # create a container to store message
        width, height = get_str_size_by_limit(message)
        
        # getting coords
        x1, y1 = self.current_x, self.current_y
        x2, y2 = x1+(width*CHAR_WIDTH), y1+((height+1)*CHAR_HEIGHT) 
        
        # draw the rectangle
        container = self.canvas_create_rounded_rectangle(
            canvas, 
            x1, y1, x2, y2, radius=50,
            fill=bg_color
        )

        # draw a username
        username_x, username_y = x1+(len(title)*10), y1+15
        canvas.create_text(username_x, username_y, text=title, font=self.font_message_user)

        # draw a line
        line_y = username_y + 10
        canvas.create_line(x1, line_y, x1+(width*CHAR_WIDTH), line_y)
        
        # draw a message content
        content_x = x1 + (width*6)
        content_y = y1+(height*CHAR_HEIGHT)
        canvas.create_text(content_x, content_y, text=format_str_with_limit(message, limit=20), font=self.font_message_content)

        # prepare position for the next message
        self.current_y = y2 + MESSAGE_MARGIN_BOTTOM

    def canvas_create_rounded_rectangle(self, canvas, x1, y1, x2, y2, radius=30, **kwargs) :
        """
            Draw a rounded rect at the specified position

            CREDIT
                - stackoverflow
        """        
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1
        ]

        return canvas.create_polygon(points, **kwargs, smooth=True)

    def _setup_form(self):
        
        from tkinter.scrolledtext import ScrolledText

        frame = tk.Frame(self)
        self.text_edit = ScrolledText(frame, width=100, height=5)
        self.btn_send = tk.Button(frame, text="Envoyer")
        
        self.text_edit.grid(column=0, row=0, rowspan=3)
        self.btn_send.grid(column=1, row=1, padx=5)

        frame.grid(column=0, row=2, sticky='nsew')

from math import ceil

def get_str_size_by_limit(s :str, limit :int = 20) -> tuple[int, int]:
    
    """
        RETURN 
            (width, height) of the given string s
    """
    width = (len(s), limit)[len(s)>limit]
    return (width, ceil(len(s) / limit))

def format_str_with_limit(s :str, limit :int, limiter='\n') -> str:

    _s = ''
    i = 0
    for c in s:
        _s += c
        i += 1
        if i == limit:
            i = 0
            _s += limiter
    return _s

if __name__ == '__main__':

    root = tk.Tk()
    client = ClientMainUi(root)
    center_window(root, client.width, client.height)
    client.pack()
    root.mainloop()
    
