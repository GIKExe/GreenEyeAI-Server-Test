from time import sleep  # noqa: F401

from server.inet import Socket
from server.request import Request
from server.logging import info, warn


socket = Socket()
socket.connect(('localhost', 5000))
socket.settimeout(None)

# req = Request('POST', '/api/command/mode')
# req.header('Connection', 'keep-alive')
# req.json({'mode': 'manual'})
# req.to_socket(socket)

# req = Request.from_socket(socket)
# if req is None:
# 	warn('Входящий запрос неверный')
# 	exit()
# info('\n', req.to_text(), sep='')


req = Request('POST', '/api/command/light')
req.header('Connection', 'close')
req.json({'state': 'on'})
req.to_socket(socket)

req = Request.from_socket(socket)
if req is None:
	warn('Входящий запрос неверный')
	exit()
info('\n', req.to_text(), sep='')




# from time import sleep

# from server.cluster import Cluster, File
# from server.logging import info, warn, error  # noqa: F401


# cl = Cluster('site')
# if cl is None:
# 	error('Кластер не создан!')
# 	exit()
	
# cl.update()
# print('/admin/login.html' in cl)