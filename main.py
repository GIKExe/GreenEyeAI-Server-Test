from socket import socket as Socket, AF_INET, SOCK_STREAM
# from time import sleep
from local.utils.logging import info, warn
from local.utils.threads import non_blocking
from local.http.request import Request


def accepting(socket: Socket) -> None:
	running: bool = True
	while running:
		client: Socket
		ip: str
		port: int
		client, (ip, port) = socket.accept()
		processing(client, ip, port) # не блокирует поток


@non_blocking
def processing(client: Socket, ip: str, port: int) -> None:
	info(f'Подключился клиент: {ip}:{port}')
	client.settimeout(5.0)
	running: bool = True
	while running:
		req: Request = Request.from_socket(client)
		if req is None: 
			warn(f'Запрос не верный для HTTP, отключение: {ip}:{port}')
		running = False
	client.close()


def main() -> None:
	# серверный сокет
	info('Запуск приложения')
	socket: Socket = Socket(AF_INET, SOCK_STREAM)
	socket.bind(('0.0.0.0', 5000))
	socket.listen()
	accepting(socket) # блокирует поток


if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		info("Принудительная остановка приложения")
	except:
		raise
