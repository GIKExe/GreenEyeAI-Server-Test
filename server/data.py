from typing import Any


class Data(dict[str, Any]):
	def __init__(self) -> None:
		super().__init__()

	def __getattr__(self, key: str) -> Any | None:
		if key in self:
			return super().__getitem__(key)
		return None

	def __setattr__(self, key: str, value: Any) -> None:
		super().__setitem__(key, value)

	def __getitem__(self, key: str) -> Any | None:
		if key in self:	
			return super().__getitem__(key)
		return None
	
	def __setitem__(self, key: str, value: Any) -> None:
		super().__setitem__(key, value)
