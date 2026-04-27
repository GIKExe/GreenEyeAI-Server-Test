from time import sleep
from random import randint 

from server.inet import Socket
from server.request import Request
from server.data import Data

socket = Socket()
socket.connect(('localhost', 5000))
socket.settimeout(None)

req = Request('POST', '/esp/sensors')
req.headers['Connection'] = 'keep-alive'
while True:
  req.json({'temperature': randint(-33, 60)})
  socket.send(req.to_bytes())
  res = Request.from_socket(socket)
  sleep(7)