# coding:utf-8

from client.console import ClientConsole
from client.gui import ClientGUI

def description(app_name) -> str :
    return f"""
    {app_name} is a litte real time chat app with socket
    
    """

def usage(script_name) -> str :
    return f"""
    
    USAGE: {script_name} -h HOST -p PORT <mode>

    HOST - The server host
    PORT - the server host port

    """

if __name__ == '__main__':

    from sys import argv, exit
    from constants import APP_NAME

    print(description(APP_NAME))

    if len(argv) < 3:

        print(usage(argv[0]))
        exit(-1)

    client = ClientGUI(title=APP_NAME, host=argv[1], port=argv[2])
    client.start()        
    