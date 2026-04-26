from threading import Thread
from functools import wraps
from typing import Callable, Any


def non_blocking(func: Callable[..., Any]) -> Callable[..., None]:
	@wraps(func)
	def wrapper(*args, **kwargs) -> None:
		Thread(target=func, args=args, kwargs=kwargs, daemon=True).start()
	return wrapper