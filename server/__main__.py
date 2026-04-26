
from .server import Server
from .response import Response
from .request import Request

server = Server()

@server.path('/')
def __001(req: Request) -> Response:
	return Response(200).text('Домашняя страничка')

def name_of_the_func(req: Request) -> Response:
	return Response(200).text('Отложенная функция')

server.path('/test')(name_of_the_func)
server.start()