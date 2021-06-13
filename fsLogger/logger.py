# Builtin modules
from __future__ import annotations
import re
from typing import Dict, Tuple, Any, Union, Callable, Optional
from functools import partial
from time import time
# Local modules
# Program
class Logger:
	name:str
	filterChangeTime:float
	lastFilterLevel:int
	trace:Optional[Callable]
	debug:Optional[Callable]
	info:Optional[Callable]
	warn:Optional[Callable]
	warning:Optional[Callable]
	error:Optional[Callable]
	critical:Optional[Callable]
	fatal:Optional[Callable]
	__slots__ = (
		"name", "filterChangeTime", "lastFilterLevel", "trace", "debug",
		"info", "warn", "warning", "error", "critical", "fatal"
	)
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
		self.trace    = partial(self._emit, Levels.getLevelIDByName("TRACE"))
		self.debug    = partial(self._emit, Levels.getLevelIDByName("DEBUG"))
		self.info     = partial(self._emit, Levels.getLevelIDByName("INFO"))
		self.warn     = partial(self._emit, Levels.getLevelIDByName("WARNING"))
		self.warning  = self.warn
		self.error    = partial(self._emit, Levels.getLevelIDByName("ERROR"))
		self.critical = partial(self._emit, Levels.getLevelIDByName("CRITICAL"))
		self.fatal    = self.critical
	def getChild(self, name:str) -> Logger:
		return Logger("{}{}{}".format(self.name, LoggerManager.groupSeperator, name))
	def isFiltered(self, levelID:Union[int, str]) -> bool:
		if self.filterChangeTime != LoggerManager.filterChangeTime:
			self.filterChangeTime, self.lastFilterLevel = LoggerManager.getFilterData(self.name)
		if isinstance(levelID, str):
			levelID = Levels.parse(levelID)
		return levelID >= self.lastFilterLevel
	def _emit(self, levelID:int, message:str, *args, **kwargs) -> None:
		if self.isFiltered(levelID):
			LoggerManager.emit(self.name, levelID, time(), message, args, kwargs)

# Finalizing imports
from .levels import Levels
from .loggerManager import LoggerManager
