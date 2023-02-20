
from socket import socket

from models.user import User

class Connection:

    def __init__(self, user: User, sock :socket, host :str, port :int) -> None:
        
        self.user = user
        self.sock = sock
        self.addr = (host, port)
    
    def __str__(self) -> str:
        return f'User<{self.user.username}, {self.addr}>'
        

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
        
        return None
    
    def get_connection_by_addr(self, host:str, port:int) -> Connection | None:

        for conn in self.connections:
            if (host, port) == conn.addr:
                return conn
        
        return None
    
    
    def get_connection_by_sock(self, sock) -> Connection | None:

        for conn in self.connections:
            if conn.sock == sock:
                return conn
        return None

    def remove_connection(self, addr):

        conn = self.get_connection_by_addr(*addr)
        self.connections.remove(conn)
    
    def remove_connection_by_sock(self, sock):

        conn = self.get_connection_by_sock(sock)
        if conn is not None:
            self.connections.remove(conn)

    def get_all(self) -> list[Connection]:
        return self.connections

    #
    def exists_user_connection(self, user :str) -> bool :

        for conn in self.connections:
            if conn.user.username.lower() == user.lower():
                return True
        
        return False