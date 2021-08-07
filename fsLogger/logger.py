# Builtin modules
from __future__ import annotations
from typing import Dict, Any, Union
from time import time
# Third party modules
# Local modules
from .globHandler import _GlobHandler
from .levels import Levels
# Program
class Logger:
	name:str
	filterChangeTime:float
	lastFilterLevel:int
	__slots__ = ( "name", "filterChangeTime", "lastFilterLevel" )
	def __init__(self, name:Union[str, Logger]):
		if isinstance(name, Logger):
			name = name.name
		self.__setstate__({ "name":name, "filterChangeTime":0, "lastFilterLevel":0 })
	def __getstate__(self) -> Dict[str, Any]:
		return {
			"name":self.name,
			"filterChangeTime":self.filterChangeTime,
			"lastFilterLevel":self.lastFilterLevel,
		}
	def __setstate__(self, states:Dict[str, Any]) -> None:
		self.name = states["name"]
		self.filterChangeTime = states["filterChangeTime"]
		self.lastFilterLevel = states["lastFilterLevel"]
	def getChild(self, name:str) -> Logger:
		return Logger("{}{}{}".format(self.name, _GlobHandler.getGroupSeperator(), name))
	def isFiltered(self, levelID:Union[int, str]) -> bool:
		if self.filterChangeTime != _GlobHandler.getFilterChangeTime():
			self.filterChangeTime, self.lastFilterLevel = _GlobHandler.getFilterData(self.name)
		if isinstance(levelID, str):
			levelID = Levels.parse(levelID)
		return levelID >= self.lastFilterLevel
	def trace(self, message:str, *args:Any, **kwargs:Any) -> None:
		levelID = Levels.getLevelIDByName("TRACE")
		if self.isFiltered(levelID):
			_GlobHandler.emit(self.name, levelID, time(), message, args, kwargs)
		return None
	def debug(self, message:str, *args:Any, **kwargs:Any) -> None:
		levelID = Levels.getLevelIDByName("DEBUG")
		if self.isFiltered(levelID):
			_GlobHandler.emit(self.name, levelID, time(), message, args, kwargs)
		return None
	def info(self, message:str, *args:Any, **kwargs:Any) -> None:
		levelID = Levels.getLevelIDByName("INFO")
		if self.isFiltered(levelID):
			_GlobHandler.emit(self.name, levelID, time(), message, args, kwargs)
		return None
	def warn(self, message:str, *args:Any, **kwargs:Any) -> None:
		levelID = Levels.getLevelIDByName("WARNING")
		if self.isFiltered(levelID):
			_GlobHandler.emit(self.name, levelID, time(), message, args, kwargs)
		return None
	def warning(self, message:str, *args:Any, **kwargs:Any) -> None:
		levelID = Levels.getLevelIDByName("WARNING")
		if self.isFiltered(levelID):
			_GlobHandler.emit(self.name, levelID, time(), message, args, kwargs)
		return None
	def error(self, message:str, *args:Any, **kwargs:Any) -> None:
		levelID = Levels.getLevelIDByName("ERROR")
		if self.isFiltered(levelID):
			_GlobHandler.emit(self.name, levelID, time(), message, args, kwargs)
		return None
	def critical(self, message:str, *args:Any, **kwargs:Any) -> None:
		levelID = Levels.getLevelIDByName("CRITICAL")
		if self.isFiltered(levelID):
			_GlobHandler.emit(self.name, levelID, time(), message, args, kwargs)
		return None
	def fatal(self, message:str, *args:Any, **kwargs:Any) -> None:
		levelID = Levels.getLevelIDByName("CRITICAL")
		if self.isFiltered(levelID):
			_GlobHandler.emit(self.name, levelID, time(), message, args, kwargs)
		return None
