from __future__ import annotations
from typing import Callable
from socket import socket as Socket, AF_INET, SOCK_STREAM
from time import sleep

from .logging import info, warn
from .threads import nonblocking
from .request import Request
from .response import Response
from .data import Data
from .database import DataBase

CALLBACK_TYPE = Callable[['Server', Request], Response]

class Server:
	data: Data
	host: str
	port: int
	socket: Socket
	paths: dict[str, dict[str, CALLBACK_TYPE]]
	database: DataBase | None

	def __init__(self,
		data: Data,
		host: str = '0.0.0.0',
		port: int = 5000,
		database: DataBase | None = None,
	) -> None:
		self.data = data
		self.database = database
		self.paths = dict()
		self.host = host
		self.port = port

	# используется для добавления обработчика на путь
	def path(self, method: str, path: str) -> Callable[[CALLBACK_TYPE], None]:
		def wrapper(func: CALLBACK_TYPE):
			if path not in self.paths:
				self.paths[path] = dict()
			self.paths[path][method] = func
		return wrapper
		
	@nonblocking
	def accepting(self) -> None:
		running: bool = True
		while running:
			client: Socket
			ip: str
			port: int
			client, (ip, port) = self.socket.accept()
			self.processing(client, ip, port) # не блокирует поток

	@nonblocking
	def processing(self, client: Socket, ip: str, port: int) -> None:
		info(f'Подключение: {ip}:{port}')
		client.settimeout(5.0)
		running: bool = True
		while running:
			try:
				req = Request.from_socket(client)
			except TimeoutError, ConnectionResetError:
				running = False
				continue
			except:
				raise

			if req is None:
				running = False
				warn(f'Неверный HTTP: {ip}:{port}')
				client.send(Response(400).to_bytes())
				continue

			if req.headers['Connection'] == 'close':
				running = False
			elif req.headers['Connection'] == 'keep-alive':
				client.settimeout(60.0)

			if req.path not in self.paths:
				client.send(Response(404)
					.text("404: Страница не найдена")
					.header('Connection', 'keep-alive' if running else 'close')
					.to_bytes())
				continue

			if req.method not in self.paths[req.path]:
				client.send(Response(400)
					.header('Connection', 'keep-alive' if running else 'close')
					.to_bytes())
				continue
	
			res = self.paths[req.path][req.method](self, req)
			res.header('Connection', 'keep-alive' if running else 'close')
			client.send(res.to_bytes())

		info(f'Отключение: {ip}:{port}')
		client.close()

	def start(self) -> None:
		info('Запуск сервера')
		self.socket: Socket = Socket(AF_INET, SOCK_STREAM)
		self.socket.bind((self.host, self.port))
		self.socket.listen()
		self.accepting() # не блокирует поток

		try:
			while True:
				if self.database is not None and self.database.update():
					continue
				sleep(0.5)
		except KeyboardInterrupt:
			info("Принудительная остановка сервера")
			if self.database is not None:
				self.database.close()
		except:
			raise