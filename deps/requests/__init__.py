#coding:utf-8

from deps.requests._types import *
from json.encoder import JSONEncoder
from json.decoder import JSONDecoder

from socket import socket

class Requests:

    """
        Request class

        - headers
        content-type
        content-size
        (sender, sender_port)
        (receiver, receiver_port)

        - options
        content
    """

    def __init__(self, type: RequestType, headers: dict = {}, options: dict = {}) -> None:
        
        self.type = type
        self.headers = headers 
        self.options = options


    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "headers": self.headers,
            "options": self.options
        }
    
    
    def to_JsonString(self) -> str:
        return JSONEncoder().encode(self.to_dict())
    

    def from_dict(req: dict):
        return Requests(
            type    =   req["type"], 
            headers =   req["headers"],
            options =   req["options"]
        )

    def __str__(self) -> str:
        return self.to_JsonString()

    def from_JsonString(req: str):
        return Requests.from_dict(JSONDecoder().decode(req))

class Response(Requests):
    
    def __init__(self, type: ResponseType, headers: dict = {}, options: dict = {}) -> None:
        super().__init__(type, headers, options)

class RequestModel:

    def __init__(self, sock: socket = None) -> None:
        self._sock = sock
        self.sender = None
    
    @property
    def sock(self) -> socket:
        return self._sock

    def setSock(self, sock :socket) -> None:
        self._sock = sock

    def sender_update(self, sock):
        self.sender = sock.getsockname()

    def send(self, req : Requests, use_receiver = False, feedback:bool = False, sender = None, use_sock :bool = False, sock : socket = None) -> Response | None:

        # use another socket to send or receive data
        if use_sock and sock != None:
            _sock = sock
        else:
            _sock = self._sock

        # update the sender for the request
        if sender == None:
            self.sender_update(_sock)
        else:
            self.sender = tuple(sender)

        req.headers["sender"] = self.sender

        if use_receiver:
            receiver, port = tuple(req.headers["receiver"])
            _sock.sendto(bytes(req.to_JsonString().encode("UTF-8")), (receiver, int(port)))
        else:
            _sock.send(bytes(req.to_JsonString().encode("UTF-8")))

        print("[+] New request send : " + req.type)

        # to view later
        if feedback:
            return self.get()

    
    def get(self, size: int = 2048, sock : socket = None, use_sock :bool = False) -> Response:

        # get response
        if use_sock and sock != None:
            data = sock.recv(size)
        else:
            data = self.sock.recv(size)
        # format response
        response = Requests.from_JsonString(data.decode("UTF-8").strip())
        print(f"[+] New response from {response.headers}:" + response.type)
        
        return response

class RequestsFactory:

    def make_request(self, _type: RequestType, headers = {}, options = {}) -> Requests:
        return Requests(
            type        = _type,
            headers     = headers,
            options     = options
        )
        

    def make_auth_request(self, headers = {}, options = {}) -> Requests:
        return self.make_request(REQUEST_AUTH_CLIENT, headers, options)

    def make_simple_request(self, headers = {}, options = {}) -> Requests:
        return self.make_request(REQUEST_SEND_TEXT, headers, options)

    def make_kill_server_request(self, reason) -> Requests:
        return self.make_request(REQUEST_STOP_SERVER, options={"content": reason})

