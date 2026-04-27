from __future__ import annotations
from typing import Callable
from socket import socket as Socket, AF_INET, SOCK_STREAM
from time import sleep
import sqlite3
from sqlite3 import Cursor
from threading import RLock

from .logging import info, warn
from .threads import nonblocking
from .request import Request
from .response import Response
from .data import Data


CALLBACK_TYPE = Callable[[Data, Request], Response]

class Server:
	data: Data
	host: str
	port: int
	socket: Socket
	paths: dict[str, CALLBACK_TYPE]
	func: Callable[[], None]

	def __init__(self,
		data: Data,
		host: str = '0.0.0.0',
		port: int = 5000,
		db_path: str = 'main.db',
		main: Callable[[], None] | None = None
	) -> None:
		self.data = data
		self.data.cursor = list()
		self.data.cursor_lock = RLock()
		self.paths = dict()
		self.host = host
		self.port = port
		self.db_conn = sqlite3.connect(db_path, isolation_level=None)
		self.db_curs = self.db_conn.cursor()
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
				res = self.paths[req.path](self.data, req)
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
				if len(self.data.cursor) == 0:
					sleep(0.1)
				else:
					with self.data.cursor_lock:
						self.db_curs.execute(*self.data.cursor.pop(0))
		except KeyboardInterrupt:
			info("Принудительная остановка сервера")
		except:
			raise

	def main(self, main: Callable[[], None]) -> Server:
		self.func = main
		return self