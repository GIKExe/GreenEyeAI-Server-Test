from server import Server, Request, Response
from server.cluster import File


def web_gmod_path(server: Server, req: Request) -> Response:
	with server.data.mode_lock:
		return Response(200).json({
			'mode': server.data.mode
		})


def web_smod_path(server: Server, req: Request) -> Response:
	data = req.get_json()
	if data is None:
		return Response(400)
	if 'mode' not in data:
		return Response(400)
	if data['mode'] not in ['auto', 'manual']:
		return Response(400)
	with server.data.mode_lock:
		server.data.mode = data['mode']
	return Response(200)


def web_gidx_path(server: Server, req: Request) -> Response:
	if '/index.html' in server.cluster:
		obj = server.cluster['/index.html']
		if type(obj) is File:
			return Response(200).bytes(obj.read())
	return Response(404)


def web_gadm_path(server: Server, req: Request) -> Response:
	# if '/admin.html' in server.cluster:
	# 	obj = server.cluster['/admin.html']
	# 	if type(obj) is File:
	# 		return Response(200).bytes(obj.read())

	# типо проверку не прошли, перенаправим ка на логин
	return Response(302).header('Location', '/admin/login.html')