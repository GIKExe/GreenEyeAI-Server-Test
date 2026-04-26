from __future__ import annotations
from socket import socket as Socket, AF_INET, SOCK_STREAM
from time import sleep
from typing import Callable

from .logging import info, warn
from .threads import nonblocking
from .request import Request
from .response import Response


CALLBACK_TYPE = Callable[[Request], Response]

class Server:
	host: str
	port: int
	socket: Socket
	paths: dict[str, CALLBACK_TYPE]
	func: Callable[[], None]

	def __init__(self, host: str = '0.0.0.0', port: int = 5000, main: Callable[[], None] | None = None) -> None:
		self.paths = dict()
		self.host = host
		self.port = port
		self.func = main if main else (lambda: None)

	# используется для добавления обработчика на путь
	def path(self, path: str) -> Callable[[CALLBACK_TYPE], None]:
		def wrapper(func: CALLBACK_TYPE):
			self.paths[path] = func
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
				info(f'Отключение: {ip}:{port}')
				running = False
				continue
			except:
				raise

			if req is None: 
				warn(f'Запрос не верный для HTTP, отключение: {ip}:{port}')
				running = False
				continue

			if req.path in self.paths:
				res = self.paths[req.path](req)
			else:
				res = Response(404).text("404: Страница не найдена")
			client.send(res.to_bytes())

			if req.headers['Connection'] == 'close':
				running = False
			elif req.headers['Connection'] == 'keep-alive':
				client.settimeout(60.0)

		client.close()

	def start(self) -> None:
		info('Запуск приложения')
		self.socket: Socket = Socket(AF_INET, SOCK_STREAM)
		self.socket.bind((self.host, self.port))
		self.socket.listen()
		self.accepting() # не блокирует поток

		try:
			while True:
				sleep(1)
		except KeyboardInterrupt:
			info("Принудительная остановка сервера")
		except:
			raise

	def main(self, main: Callable[[], None]) -> Server:
		self.func = main
		return self