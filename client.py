# coding:utf-8

from client.console import ClientConsole
from client.gui import ClientGUI

def description(app_name) -> str :
    return f"""
    {app_name} is a litte real time chat app with socket
    """

def usage() -> str :
    return f"""
    HOST - The server host
    PORT - the server host port
    """

def parser(script_name):
    
    """
        Parser for args im command line
    """

    import argparse

    _parser = argparse.ArgumentParser(
        script_name,
        description=description(APP_NAME),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    _parser.add_argument(
        'HOST', action='store',
        help='Port to connect the server', 
        default='127.0.0.1', type=str
    )

    _parser.add_argument(
        'PORT', action='store',
        help='Port to connect the server', 
        default=1234, type=int
    )

    _parser.add_argument(
        '--console', action='store_true',
        help='To Open Client in gui mode'
    )
    
    return _parser

if __name__ == '__main__':

    from sys import argv, exit
    from constants import APP_NAME, MODE_CONSOLE, MODE_UI

    try:

        args = parser('client.py').parse_args(argv[1:])

        client = ClientGUI(title=APP_NAME, host=args.HOST, port=args.PORT)
        
        # if user request console
        if args.console:
            client.start(mode=MODE_CONSOLE)
        else:
            client.start(mode=MODE_UI)
            
    except:
        print('')
    