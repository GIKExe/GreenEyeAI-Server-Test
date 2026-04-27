
from server import Server, Request, Response, Data
from server.logging import info


data = Data()
data.sensors = list()
server = Server(data)

@server.path('/')
def index_path(d: Data, req: Request) -> Response:
	return Response(200).text('Домашняя страничка')

def test_path(d: Data, req: Request) -> Response:
	return Response(200).text(req.get_http_body().replace('\r\n', '<br>'))

def esp_sensors_path(d: Data, req: Request) -> Response:
	data: dict = req.get_json()
	if 'temperature' in data and d.sensors is not None:
		d.sensors.append(data['temperature'])
	return Response(200)

server.path('/test')(test_path)
server.path('/esp/sensors')(esp_sensors_path)
server.start()

print(data)