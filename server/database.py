from __future__ import annotations
import sqlite3
from sqlite3 import Cursor, Connection
from threading import RLock
from typing import Any


class DataBase:
	lock: RLock
	connection: Connection
	cursor: Cursor
	commands: list[Any]

	def __init__(self, path: str) -> None:
		self.lock = RLock()
		self.connection = sqlite3.connect(path, isolation_level=None)
		self.cursor = self.connection.cursor()
		self.commands = list()
	
	def execute(self, sql: str, parameters: tuple = ()) -> DataBase:
		'''отложенное выполнение, подходит для многопотока'''
		with self.lock:
			self.commands.append((sql, parameters))
		return self

	def update(self) -> bool:
		if len(self.commands) > 0:
			with self.lock:
				args = self.commands.pop(0)
				self.cursor.execute(*args)
			return True
		return False
	
	def close(self) -> None:
		self.cursor.close()
		self.connection.close()