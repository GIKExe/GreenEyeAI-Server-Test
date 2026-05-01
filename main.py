import uuid
from threading import Lock

from server import Server, Request, Response
from server import Data, DataBase
from server.cluster import Cluster
from server.logging import info, warn, error  # noqa: F401

from esp_paths import esp_sens_path, esp_gcmd_path, esp_dcmd_path
from web_paths import web_gmod_path, web_smod_path
from web_paths import web_gidx_path, web_gadm_path, web_galn_path, web_paln_path
from web_paths import web_acwr_path, web_aclt_path, web_acfn_path
from web_paths import web_gdbr_path


data = Data() # общие переменные и тд
data.commands = list()
data.commands_lock = Lock()
data.mode = 'manual' # или auto
data.mode_lock = Lock()
data.token = str(uuid.uuid4())
info('Токен авторизации:', data.token)


database = DataBase('main.db')
database.execute('''
	CREATE TABLE IF NOT EXISTS sensors (
		temperature FLOAT NOT NULL,
		humidity FLOAT NOT NULL
	)
''')
database.execute('''
	CREATE TABLE IF NOT EXISTS light (
		timestamp REAL NOT NULL,
		state BOOLEAN NOT NULL
	)
''')
database.execute('''
	CREATE TABLE IF NOT EXISTS water (
		timestamp REAL NOT NULL,
		state BOOLEAN NOT NULL
	)
''')
database.execute('''
	CREATE TABLE IF NOT EXISTS fan (
		timestamp REAL NOT NULL,
		state BOOLEAN NOT NULL
	)
''')


cluster = Cluster('site')
if cluster is None:
	error('Кластер повреждён!')
	exit()
server = Server(data, database, cluster)


@server.path('GET', '/me')
def me_path(server: Server, req: Request) -> Response:
	return Response(200).text(req.to_body().replace('\r\n', '<br>'))


@server.path('GET', '/ping')
def ping_path(server: Server, req: Request) -> Response:
	return Response(200)


server.path('POST', '/api/esp/sensors'  )(esp_sens_path)
server.path('GET',  '/api/esp/command'  )(esp_gcmd_path)
server.path('POST', '/api/esp/command'  )(esp_dcmd_path)

server.path('GET',  '/api/command/mode' )(web_gmod_path)
server.path('POST', '/api/command/mode' )(web_smod_path)

server.path('POST', '/api/command/water')(web_acwr_path)
server.path('POST', '/api/command/light')(web_aclt_path)
server.path('POST', '/api/command/fan'  )(web_acfn_path)

server.path('GET',  '/'                 )(web_gidx_path)
server.path('GET',  '/admin'            )(web_gadm_path)
server.path('GET',  '/admin.html'       )(web_gadm_path)
server.path('GET',  '/admin/login'      )(web_galn_path)
server.path('POST', '/api/admin/login'  )(web_paln_path)
server.path('GET',  '/api/web/db'       )(web_gdbr_path)

server.start()