from time import sleep  # noqa: F401
from random import choice  # noqa: F401

from server.inet import Socket
from server.request import Request
from server.logging import info, warn, error # noqa: F401


socket = Socket()
socket.connect(('localhost', 5000))
socket.settimeout(None)

while True:
	Request('GET', '/ping').to_socket(socket)
	res = Request.from_socket(socket)
	if res is None:
		warn('Входящий запрос неверный')
		break
	info(res.to_body())
	sleep(4.0)
