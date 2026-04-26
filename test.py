from socket import socket as Socket, timeout, AF_INET, SOCK_STREAM
from server.logging import *

socket = Socket(AF_INET, SOCK_STREAM)
socket.connect(("localhost", 5000))

