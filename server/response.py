from __future__ import annotations
import json

from .status import STATUS


class Response:
  data: bytes
  headers: dict[str, str]

  def __init__(self, status: int = 200, headers: dict[str, str] | None = None, data: bytes | None = None):
    self.status = status

    self.headers = {
      'Connection': 'close',
      'Content-Type': 'text/html; charset=utf-8',
      'Content-Length' : '0'
    }
    if headers is not None:
      for k,v in headers.items():
        self.headers[k] = v

    self.data = b''
    if data is not None:
      self.data = data

  def text(self, data: str) -> Response:
    self.headers['Content-Type'] = 'text/html; charset=utf-8'
    self.data = data.encode('utf8')
    return self

  def json(self, data: dict | list) -> Response:
    self.headers['Content-Type'] = 'application/json'
    self.data = json.dumps(data).encode('utf8')
    return self
    
  def to_bytes(self):
    self.headers['Content-Length'] = str(len(self.data))
    headers: str = '\r\n'.join([f'{k}: {v}' for k,v in self.headers.items()])
    return f'''HTTP/1.1 {self.status} {STATUS[self.status]}\r\n{headers}\r\n\r\n'''.encode('ascii') + self.data
  
