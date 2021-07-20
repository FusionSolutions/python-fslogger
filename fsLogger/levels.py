# Builtin modules
from __future__ import annotations
from typing import List, Union, Tuple
# Third party modules
# Local modules
# Program
class Levels:
	levels:List[ Tuple[int, str, str] ] = [
		(100, "DISABLED", "DIS"),
		(60, "CRITICAL", "CRI"),
		(50, "ERROR", "ERR"),
		(40, "WARNING", "WAR"),
		(30, "INFO", "INF"),
		(20, "DEBUG", "DBG"),
		(10, "TRACE", "TRC"),
	]
	@classmethod
	def addLevel(cls, id:int, name:str, shortName:str) -> None:
		assert id > 0, "ID must be higher as zero"
		cls.levels.append((id, name, shortName))
		cls.levels = sorted(cls.levels, key=lambda x: -x[0])
		return None
	@classmethod
	def removeLevel(cls, level:Union[int, str]) -> None:
		levelID = cls.parse(level)
		for i, d in enumerate(cls.levels):
			if d[0] == levelID:
				del cls.levels[i]
				return
		return None
	@classmethod
	def getLevelIDByName(cls, name:str) -> int:
		name = name.upper()
		d:Tuple[int, str, str]
		for d in cls.levels:
			if d[1] == name:
				return d[0]
		return 0
	@classmethod
	def getLevelIDByShortName(cls, shortName:str) -> int:
		shortName = shortName.upper()
		d:Tuple[int, str, str]
		for d in cls.levels:
			if d[2] == shortName:
				return d[0]
		return 0
	@classmethod
	def getLevelNameByID(cls, id:int) -> str:
		d:Tuple[int, str, str]
		for d in cls.levels:
			if d[0] == id:
				return d[1]
		raise KeyError("Levels: Unknown level: {}".format(id))
	@classmethod
	def getLevelShortNameByID(cls, id:int) -> str:
		d:Tuple[int, str, str]
		for d in cls.levels:
			if d[0] == id:
				return d[2]
		raise KeyError("Levels: Unknown level: {}".format(id))
	@classmethod
	def parse(cls, level:Union[int, str]) -> int:
		r:int
		if isinstance(level, str) and level.isdigit():
			level = int(level)
		if isinstance(level, int):
			for d in cls.levels:
				if d[0] == level:
					return level
		else:
			r = cls.getLevelIDByName(level)
			if r == 0:
				r = cls.getLevelIDByShortName(level)
			if r != 0:
				return r
		raise KeyError("Levels: Unknown level: {}".format(level))
