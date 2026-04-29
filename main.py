from threading import Lock

from server import Server, Request, Response
from server import Data, DataBase, Dir, File

from esp_paths import esp_sens_path, esp_gcmd_path, esp_dcmd_path


data = Data() # общие переменные и тд
data.commands = list()
data.commands_lock = Lock()

database = DataBase('main.db')
database.execute('''
	CREATE TABLE IF NOT EXISTS sensors (
		temperature FLOAT NOT NULL,
		humidity FLOAT NOT NULL
	)
''')
database.execute('''
	CREATE TABLE IF NOT EXISTS light (
		timestamp TIMESTAMP NOT NULL,
		state BOOLEAN NOT NULL
	)
''')
database.execute('''
	CREATE TABLE IF NOT EXISTS water (
		timestamp TIMESTAMP NOT NULL,
		state BOOLEAN NOT NULL
	)
''')
database.execute('''
	CREATE TABLE IF NOT EXISTS fan (
		timestamp TIMESTAMP NOT NULL,
		state BOOLEAN NOT NULL
	)
''')


server = Server(data, database=database)


@server.path('GET', '/me')
def me_path(server: Server, req: Request) -> Response:
	return Response(200).text(req.to_body().replace('\r\n', '<br>'))


server.path('POST', '/api/esp/sensors')(esp_sens_path)
server.path('GET', '/api/esp/command')(esp_gcmd_path)
server.path('POST', '/api/esp/command')(esp_dcmd_path)
server.start()