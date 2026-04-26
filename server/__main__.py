
from .inet import Socket
from .server import Server
from .response import Response

server = Server()

@server.path('/')
def home_page(client: Socket) -> Response:
	return Response(200).text('Домашняя страничка')

@server.path('/me')
def хуита(client: Socket) -> Response:
	ip, port = client.getpeername()
	return Response(200).json({
		"client": f"{ip}:{port}"
	})

server.start()