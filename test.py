from time import sleep
from random import randint 

from server.inet import Socket
from server.request import Request
from server.logging import info


socket = Socket()
socket.connect(('localhost', 5000))
socket.settimeout(None)

req = Request('POST', '/esp/sensors')
req.headers['Connection'] = 'keep-alive'
while True:
  data = {
    'temperature': randint(-3300, 6000) / 100,
    'humidity': randint(0, 10000) / 100
  }
  req.json(data)
  socket.send(req.to_bytes())
  info('Отправлено:', data)
  res = Request.from_socket(socket)
  sleep(10)