
from .server import Server
from .response import Response
from .request import Request
from .logging import info

server = Server()

@server.path('/')
def __001(req: Request) -> Response:
	return Response(200).text('Домашняя страничка')

def name_of_the_func(req: Request) -> Response:
	return Response(200).text(req.get_http_body().replace('\r\n', '<br>'))

def esp_sensors_path(req: Request) -> Response:
	info('Показания с датчиков:', req.data.decode('utf8'))
	return Response(200)

server.path('/test')(name_of_the_func)
server.path('/esp/sensors')(esp_sensors_path)
server.start()