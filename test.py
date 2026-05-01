from time import sleep  # noqa: F401

from server.inet import Socket
from server.request import Request
from server.logging import info, warn, error # noqa: F401


socket = Socket()
socket.connect(('localhost', 5000))
socket.settimeout(60)

# req = Request('POST', '/api/command/mode')
# req.header('Connection', 'keep-alive')
# req.json({'mode': 'manual'})
# req.to_socket(socket)

# req = Request.from_socket(socket)
# if req is None:
# 	warn('Входящий запрос неверный')
# 	exit()
# info('\n', req.to_text(), sep='')

token: str = "27459207-425d-46f6-b983-655348aca460"
state: str = "off"

req = Request('POST', '/api/command/water')
req.header('Connection', 'keep-alive')
req.json({'state': state, 'token': token})
req.to_socket(socket)

# res = Request.from_socket(socket)
# if res is None:
# 	warn('Входящий запрос неверный')
# 	exit()
# info('\n', res.to_text(), sep='')

sleep(0.1)
req = Request('POST', '/api/command/light')
req.header('Connection', 'keep-alive')
req.json({'state': state, 'token': token})
req.to_socket(socket)


sleep(0.1)
req = Request('POST', '/api/command/fan')
req.header('Connection', 'keep-alive')
req.json({'state': state, 'token': token})
req.to_socket(socket)

sleep(1)

# from time import sleep

# from server.cluster import Cluster, File
# from server.logging import info, warn, error  # noqa: F401


# cl = Cluster('site')
# if cl is None:
# 	error('Кластер не создан!')
# 	exit()
	
# cl.update()
# print('/admin/login.html' in cl)