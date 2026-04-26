from socket import socket as Socket, timeout, AF_INET, SOCK_STREAM
from local.utils.logging import *

socket = Socket(AF_INET, SOCK_STREAM)
socket.connect(("localhost", 5000))

