from socket import socket as Socket, MSG_PEEK, timeout
from functools import wraps
from .inet import *
from ..utils.logging import *


class Request:
	method: str
	path: str
	version: str
	headers: dict[str: str]
	data: bytes
	
	@staticmethod
	def from_socket(client: Socket) -> Request | None:
		req: Request = Request()
		# читаем заголовки HTTP
		data: bytes = client.recv(KiB*4, MSG_PEEK) # опасная функция
		index: int = data.find(b'\r\n\r\n')
		if index < 0:
			return None
		data: bytes = client.recv(index+4)
		data = data[:-4]
		text: str = data.decode('ascii') # опасная функция
		headers: list[str] = text.split('\r\n')

		line: str = headers.pop(0)
		method: str; path: str; version: str;
		method, path, version = line.split(' ', 2)

		if '?' in path:
			path = path.split('?', 1)[0]

		req.method = method.upper()
		req.path = path
		req.version = version.upper()

		req.headers = dict()
		for header in headers:
			header, content = header.split(': ', 1)
			req.headers[header] = content

		if 'Content-Length' in req.headers:
			...
		else:
			req.data = b''

		return req
	
	def to_bytes(self) -> bytes | None:
		line: str = ' '.join([self.method, self.path, self.version])
		text: str = '\r\n'.join([line,] + [f'{k}: {v}' for k, v in self.headers.items()])
		return text.encode('ascii') + b'\r\n\r\n' + self.data
