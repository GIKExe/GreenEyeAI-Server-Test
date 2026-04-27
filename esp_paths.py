from server import Server, Request, Response


def esp_sens_path(server: Server, req: Request) -> Response:
	data: dict = req.get_json()
	if server.database is None:
		return Response(500)
	if data and 'temperature' in data and 'humidity' in data:
		server.database.execute(
			'INSERT INTO sensors (temperature, humidity) VALUES (?, ?)',
			(data['temperature'], data['humidity'])
		)
	else:
		return Response(400).text('Не полные данные')
	return Response(200)


def esp_gcmd_path(server: Server, req: Request) -> Response:
	commands: list[tuple[int, str, str]] = server.data.commands
	command_id, device, action = (0, 'None', 'off')
	with server.data.commands_lock:
		if len(commands) > 0:
			command_id, device, action = commands[0]
	return Response(200).json({
		"queue_size": len(commands),
		"command_id": command_id,
		"device": device,
		"action": action
	})


def esp_dcmd_path(server: Server, req: Request) -> Response:
	commands: list[tuple[int, str, str]] = server.data.commands
	data = req.get_json()
	if data is None:
		return Response(400)
	if ('command_id' not in data) or ('status' not in data):
		return Response(400)
	with server.data.commands_lock:
		if len(commands) == 0:
			return Response(400)
		if data['command_id'] != commands[0][0]:
			return Response(400)
		del commands[0]
	return Response(200)