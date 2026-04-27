from threading import RLock

from server import Server, Request, Response, Data
from server.logging import info


data = Data()

server = Server(data)
server.db_curs.execute("DROP TABLE IF EXISTS sensors")
server.db_curs.execute("""
	CREATE TABLE sensors (
		temperature FLOAT NOT NULL,
		humidity FLOAT NOT NULL
	)
""")

@server.path('/')
def index_path(d: Data, req: Request) -> Response:
	return Response(200).text('Домашняя страничка')

def test_path(d: Data, req: Request) -> Response:
	return Response(200).text(req.get_http_body().replace('\r\n', '<br>'))

def esp_sensors_path(d: Data, req: Request) -> Response:
	cursor: list = d.cursor
	lock: RLock = d.cursor_lock
	data: dict = req.get_json()
	if 'temperature' in data and 'humidity' in data:
		with lock:
			cursor.append((
				'INSERT INTO sensors (temperature, humidity) VALUES (?, ?)',
				(data['temperature'], data['humidity'])
			))
	else:
		return Response(400).json({
			'status': 'error',
			'error': 'Не полные данные'
		})
	return Response(200).json({
		'status': 'ok'
	})

server.path('/test')(test_path)
server.path('/esp/sensors')(esp_sensors_path)
server.start()