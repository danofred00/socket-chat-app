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

    def __init__(self, sock: socket) -> None:
        self.sock = sock
        self.sender = sock.getsockname()
    
    def send(self, req : Requests, use_receiver = False, feedback:bool = False) -> Response | None:

        req.headers["sender"] = self.sender

        if use_receiver:
            receiver, port = tuple(req.headers["receiver"])
            self.sock.sendto(bytes(req.to_JsonString().encode("UTF-8")), (receiver, int(port)))
        else:
            self.sock.send(bytes(req.to_JsonString().encode("UTF-8")))

        print("[+] New request send : " + req.type)

        if feedback:
            return self.get()

    
    def get(self, size: int = 2048) -> Response:

        data = self.sock.recv(size)
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

