

from ast import alias


RequestType = alias(str)
REQUEST_SEND_TEXT       = 'REQUEST_SEND_TEXT'
REQUEST_AUTH_CLIENT     = 'REQUEST_AUTH_CLIENT'
REQUEST_SEND_TO_CLIENT  = 'REQUEST_SEND_TO_CLIENT'
REQUEST_STOP_SERVER     = 'REQUEST_STOP_SERVER'
REQUEST_CLIENT_QUIT     = 'REQUEST_CLIENT_QUIT'
REQUEST_GET_ALL_CLIENTS = 'REQUEST_GET_ALL_CLIENTS'
REQUEST_GET_CLIENT_INFO = 'REQUEST_GET_CLIENT_INFO'

# responses
ResponseType = alias(str)
RESPONSE_AUTH_SUCCESS    = "RESPONSE_AUTH_SUCCESS"
RESPONSE_AUTH_FAIL       = "RESPONSE_AUTH_FAIL"
RESPONSE_ALREADY_ONLINE  = "RESPONSE_ALREADY_ONLINE"
RESPONSE_CLOSE_YOURSELF  = "RESPONSE_CLOSE_YOURSELF"
RESPONSE_GET_ALL_CLIENTS = "RESPONSE_GET_ALL_CLIENTS"
RESPONSE_CLIENT_CONNECT  = "RESPONSE_CLIENT_CONNECT"
RESPONSE_GET_CLIENT_INFO = "RESPONSE_GET_CLIENT_INFO"