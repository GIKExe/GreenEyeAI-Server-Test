from threading import Thread
from functools import wraps


def non_blocking(func: function) -> function:
	@wraps(func)
	def wrapper(*args, **kwargs) -> None:
		Thread(target=func, args=args, kwargs=kwargs, daemon=True).start()
	return wrapper