from time import sleep
from random import randint 

from server.inet import Socket
from server.request import Request
from server.logging import info


socket = Socket()
socket.connect(('localhost', 5000))
socket.settimeout(None)

temperature = randint(-3300, 6000) / 100
humidity = randint(0, 10000) / 100

req = Request('POST', '/api/esp/sensors')
req.headers['Connection'] = 'keep-alive'
while True:
  temperature += randint(-20, 20) / 10
  humidity += randint(-50, 50) / 10

  if humidity < 0:
    humidity = 0
  if humidity > 100:
    humidity = 100
  if temperature < -273:
    temperature = -273

  data = {
    'temperature': temperature,
    'humidity': humidity
  }
  req.json(data)
  socket.send(req.to_bytes())
  info('Отправлено:', data)
  res = Request.from_socket(socket)
  sleep(5)