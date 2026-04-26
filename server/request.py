from __future__ import annotations
from socket import socket as Socket, MSG_PEEK
from .inet import KiB


class Request:
	method: str
	path: str
	version: str
	headers: dict[str, str]
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

		req.data = b''
		if 'Content-Length' in req.headers:
			size: int = int(req.headers['Content-Length'])
			while True:
				if (len(req.data) >= size):
					break
				req.data += client.recv(size - len(data))
	
		return req
	
	def http_body(self) -> str:
		line: str = ' '.join([self.method, self.path, self.version])
		return '\r\n'.join([line,] + [f'{k}: {v}' for k, v in self.headers.items()]) + '\r\n\r\n'
	
	def to_str(self) -> str:
		return self.http_body() + self.data.decode('utf8')
	
	def to_bytes(self) -> bytes:
		return self.http_body().encode('ascii') + self.data
