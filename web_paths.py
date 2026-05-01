from random import randint

from server import Server, Request, Response
from server.cluster import File
from server.logging import info, warn, error  # noqa: F401


def web_gmod_path(server: Server, req: Request) -> Response:
	with server.data.mode_lock:
		mode: str = server.data.mode
	return Response(200).json({
		'mode': mode
	})


def web_smod_path(server: Server, req: Request) -> Response:
	data = req.get_json()
	if data is None:
		return Response(400)
	if ('mode' not in data) or ('token' not in data):
		return Response(400)
	if data['token'] != server.data.token:
		return Response(400)
	if data['mode'] not in ('auto', 'manual',):
		return Response(400)
	with server.data.mode_lock:
		server.data.mode = data['mode']
	return Response(200)


def web_aclt_path(server: Server, req: Request) -> Response:
	with server.data.mode_lock:
		mode: str = server.data.mode
	if mode != 'manual':
		return Response(400)
	data = req.get_json()
	if data is None:
		return Response(400)
	if ('state' not in data) or ('token' not in data):
		return Response(400)
	if data['token'] != server.data.token:
		return Response(400)
	if data['state'] not in ('on', 'off',):
		return Response(400)
	with server.data.commands_lock:
		commands: list[tuple[int, str, str]] = server.data.commands
		if len(commands) >= 10:
			del commands[-1]
		commands.append((randint(0, 65535), 'light', data['state']))
	info("Команада добавлена")
	return Response(200)
	

def web_acwr_path(server: Server, req: Request) -> Response:
	with server.data.mode_lock:
		mode: str = server.data.mode
	if mode != 'manual':
		return Response(400)
	data = req.get_json()
	if data is None:
		return Response(400)
	if ('state' not in data) or ('token' not in data):
		return Response(400)
	if data['token'] != server.data.token:
		return Response(400)
	if data['state'] not in ('on', 'off',):
		return Response(400)
	with server.data.commands_lock:
		commands: list[tuple[int, str, str]] = server.data.commands
		if len(commands) >= 10:
			del commands[-1]
		commands.append((randint(0, 65535), 'water', data['state']))
	info("Команада добавлена")
	return Response(200)


def web_acfn_path(server: Server, req: Request) -> Response:
	with server.data.mode_lock:
		mode: str = server.data.mode
	if mode != 'manual':
		return Response(400)
	data = req.get_json()
	if data is None:
		return Response(400)
	if ('state' not in data) or ('token' not in data):
		return Response(400)
	if data['token'] != server.data.token:
		return Response(400)
	if data['state'] not in ('on', 'off',):
		return Response(400)
	with server.data.commands_lock:
		commands: list[tuple[int, str, str]] = server.data.commands
		if len(commands) >= 10:
			del commands[-1]
		commands.append((randint(0, 65535), 'fan', data['state']))
	info("Команада добавлена")
	return Response(200)


def web_gidx_path(server: Server, req: Request) -> Response:
	if '/index.html' in server.cluster:
		file = server.cluster['/index.html']
		if type(file) is File:
			return Response(200).html(file.read())
	return Response(404)


def web_gadm_path(server: Server, req: Request) -> Response:
	res = Response(302).header('Location', '/admin/login')

	if 'Cookie' not in req.headers:
		return res

	if 'token='+server.data.token not in req.headers['Cookie']:
		return res

	if '/admin.html' not in server.cluster:
		return Response(404)
	
	obj = server.cluster['/admin.html']
	if type(obj) is File:
		return Response(200).bytes(obj.read())
	return Response(500)


def web_galn_path(server: Server, req: Request) -> Response:
	path = '/admin/login.html'
	if path in server.cluster:
		file = server.cluster[path]
		if type(file) is File:
			return Response(200).html(file.read())
	return Response(404)


def web_paln_path(server: Server, req: Request) -> Response:
	data = req.get_json()
	if data is None:
		return Response(400)
	if ('username' not in data) or ('password' not in data):
		return Response(400)
	if (data['username'] != 'admin') or (data['password'] != 'admin123'):
		return Response(401)
	return Response(200).json({
		'token': server.data.token,
		'expires_in': 86400
	})


def web_gdbr_path(server: Server, req: Request) -> Response:
	# SELECT * FROM water
	# WHERE timestamp >= unixepoch('now') - (120);
	data = req.get_json()
	if data is None:
		return Response(400)
	if 'table' not in data:
		return Response(400)
	if data['table'] not in ('water', 'light', 'fan'):
		return Response(400)
	table = data['table'] 
	data = server.database.execute('SELECT * FROM '+table, mode=3)
	if data is None:
		return Response(400)
	return Response(200).json(data)