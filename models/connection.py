
from socket import socket

from models.user import User

class Connection:

    def __init__(self, user: User, sock :socket, host :str, port :int) -> None:
        
        self.user = user
        self.sock = sock
        self.addr = (host, port)
        

class ConnectionModel:

    def __init__(self) -> None:
        
        self.connections : list[Connection] = []
    

    def add_connection(self, conn : Connection):
        self.connections.append(conn)
    

    def create_connection(self, user: User, sock :socket, host :str, port :int):
        self.add_connection(Connection(user, sock, host, port))


    def get_connection(self, user_id) -> Connection | None :

        for conn in self.connections:
            if conn.user.id() == user_id:
                return conn
    
    def get_connection_by_addr(self, host:str, port:int) -> Connection | None:

        for conn in self.connections:
            if (host, port) == conn.addr:
                return conn