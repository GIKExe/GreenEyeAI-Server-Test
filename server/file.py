from __future__ import annotations
from os import listdir
from time import time
from os.path import getmtime, isdir, isfile, join
from typing import Callable


class File:
	time: float
	check_time: float
	raw_data: bytes
	exists: bool
	path: str

	def __init__(self, path: str) -> None:
		self.time = 0
		self.check_time = 0
		self.raw_data = b''
		self.exists = False
		self.path = path
		self.check()

	def is_exists(self) -> bool:
		return self.exists

	def check(self) -> File:
		if time() - self.check_time < 1:
			return self
		if not isfile(self.path):
			self.exists = False
			return self

		new_time = getmtime(self.path)
		if self.time != new_time:
			with open(self.path, 'rb') as file:
				self.raw_data = file.read()
			self.time = new_time
		self.check_time = time()
		self.exists = True
		return self

	def read(self):
		return self.raw_data
	
	def data(self, data: bytes) -> File:
		self.raw_data = data
		return self

	def write(self) -> File:
		with open(self.path, 'wb') as file:
			file.write(self.raw_data)
		return self


class Dir(dict):
	time: float
	check_time: float
	exists: bool

	def __init__(self, path: str) -> None:
		self.time = 0
		self.check_time = 0
		self.exists = False
		self.path = path
		self.check()

	def is_exists(self) -> bool:
		return self.exists

	# def __missing__(self, key):
	# 	if '/' not in key:
	# 		raise Exception('ошибка, такого ключа не нет')
	# 	key, path = key.split('/', 1)
	# 	if key not in self:
	# 		raise Exception('ошибка, такого ключа не нет')
	# 	return self[key][path]

	# def __contains__(self, key: str) -> bool:
	# 	return key in self
			
	def check(self) -> None:
		if time() - self.check_time < 5:
			return
		if not isdir(self.path):
			self.exists = False
			return

		name: str
		obj: Dir | File
		for name, obj in list(self.items()):
			if obj == self:
				continue
			obj.check()
			if not obj.is_exists():
				del self[name]

		new_time = getmtime(self.path)
		if self.time != new_time:
			for name in listdir(self.path):
				if name in self.keys():
					continue
				path = join(self.path, name)
				if isdir(path):
					self[name] = Dir(path)
				elif isfile(path):
					self[name] = File(path)
			self.time = new_time
		self.check_time = time()
		return
	
	def display(self, tab: str = '', add: str | None = '  ', func: Callable[..., None] = print) -> None:
		'''аргумсент add позволяет задать добавляемый отступ во вложенных директориях, 
		но если он задан как None то функция отображает полные пути до файлов.'''
		for k,v in self.items():
			if (type(v) is File) or (add is not None):
				func(tab+k)
			if type(v) is not Dir:
				continue
			v.display(tab+(k+'/' if add is None else add), add, func)


if __name__ == "__main__":
	d = Dir('./')
	d.display(add=None)
