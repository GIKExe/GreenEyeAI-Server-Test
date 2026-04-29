from time import sleep  # noqa: F401

from server.inet import Socket
from server.request import Request
from server.logging import info, warn


socket = Socket()
socket.connect(('localhost', 5000))
socket.settimeout(None)

req = Request('GET', '/api/web/mode')
req.header('Connection', 'keep-alive')
req.to_socket(socket)
req = Request.from_socket(socket)
if req is None:
	warn('1 Входящий запрос неверный')
	exit()
info(req.to_text())

req = Request('POST', '/api/web/mode')
req.header('Connection', 'keep-alive')
req.json({'mode': 'manual'})
req.to_socket(socket)
req = Request.from_socket(socket)
if req is None:
	warn('2 Входящий запрос неверный')
	exit()
info(req.to_text())

req = Request('GET', '/api/web/mode')
req.header('Connection', 'close')
req.to_socket(socket)
req = Request.from_socket(socket)
if req is None:
	warn('3 Входящий запрос неверный')
	exit()
info(req.to_text())
