__all__ = ['Socket', 'KiB', 'MiB', 'GiB']
from socket import socket as Socket

KiB = 1024
MiB = KiB**2
GiB = KiB**3
