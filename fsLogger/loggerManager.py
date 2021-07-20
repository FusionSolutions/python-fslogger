# Builtin modules
from __future__ import annotations
import sys, atexit, traceback
from datetime import datetime
from time import time, monotonic
from threading import RLock
from typing import Dict, List, Any, cast, TextIO, Union, Tuple, Optional
# Third party modules
# Local modules
# Program
DEF_FILTER:List[Dict[str, Any]] = [{ "*":"TRACE" }]
DEF_FORMAT = "[{levelshortname}][{date}][{name}] : {message}\n"
DEF_DATE = "%Y-%m-%d %H:%M:%S.%f"

class LoggerManager:
	lock:RLock = RLock()
	handler:Optional[LoggerManager] = None
	filterChangeTime:float = monotonic()
	groupSeperator:str = "."
	@staticmethod
	def getLogger(name:str) -> Logger:
		return Logger(name)
	@staticmethod
	def getFilterData(name:str) -> Tuple[float, int]:
		if isinstance(LoggerManager.handler, LoggerManager):
			return LoggerManager.handler._getFilterData(name)
		return LoggerManager.filterChangeTime, 0
	def _getFilterData(self, name:str) -> Tuple[float, int]:
		return (
			self.filterChangeTime,
			self.filter.getFilteredID(
				name.split(self.groupSeperator)
			)
		)
	@staticmethod
	def emit(name:str, levelID:int, timestamp:float, message:Any, _args:Tuple[Any, ...], _kwargs:Dict[str, Any]) -> None:
		if isinstance(LoggerManager.handler, LoggerManager):
			LoggerManager.handler._emit(name, levelID, timestamp, message, _args, _kwargs)
		return None
	def _emit(self, name:str, levelID:int, timestamp:float, message:Any, _args:Tuple[Any, ...], _kwargs:Dict[str, Any]) -> None:
		parsedMessage = self.messageFormatter(name, levelID, timestamp, message, _args, _kwargs)
		with self.lock:
			for handler in self.modules:
				try: handler.emit(parsedMessage)
				except: pass
	@staticmethod
	def extendFilter(data:Union[List[Any], str, Filter]) -> None:
		if isinstance(LoggerManager.handler, LoggerManager):
			LoggerManager.handler._extendFilter(data)
		return None
	def _extendFilter(self, data:Union[List[Any], str, Filter]) -> None:
		filter = Filter(0)
		if isinstance(data, list):
			filter = FilterParser.fromJson(data)
		elif isinstance(data, str):
			filter = FilterParser.fromString(data)
		assert isinstance(filter, Filter)
		self.filter.extend(filter)
	@staticmethod
	def close() -> None:
		if isinstance(LoggerManager.handler, LoggerManager):
			LoggerManager.handler._close()
		return None
	def __init__(self, filter:Union[List[Any], str, Filter]=DEF_FILTER, messageFormat:str=DEF_FORMAT, dateFormat:str=DEF_DATE,
	defaultLevel:Union[int, str]="WARNING", hookSTDOut:bool=True, hookSTDErr:bool=True):
		if isinstance(self.handler, LoggerManager):
			raise RuntimeError("LoggerManager already initialized")
		LoggerManager.handler = self
		self.delta:float = monotonic()
		self.messageFormat:str = messageFormat
		self.dateFormat:str = dateFormat
		self.modules:List[ModuleBase] = []
		self.filter:Filter = Filter(Levels.parse(defaultLevel))
		self._extendFilter(filter)
		self._stderr:TextIO = sys.stderr
		self._stdout:TextIO = sys.stdout
		self._excepthook:Any = sys.excepthook
		if hookSTDErr:
			sys.stderr = cast(TextIO, STDErrModule())
			sys.excepthook = lambda *a: sys.stderr.write("".join(traceback.format_exception(*a)))
		if hookSTDOut:
			sys.stdout = cast(TextIO, STDOutModule())
		atexit.register(self.close)
	def __del__(self) -> None:
		self._close()
		return None
	def _close(self) -> None:
		for module in self.modules:
			try:
				module.close()
			except:
				pass
		self.modules.clear()
		if isinstance(sys.stderr, STDErrModule):
			sys.stderr.forceFlush()
			sys.stderr = self._stderr
		if isinstance(sys.stdout, STDOutModule):
			sys.stdout.forceFlush()
			sys.stdout = self._stdout
		LoggerManager.handler = None
		return None
	def messageFormatter(self, name:str, levelID:int, timestamp:float, message:str,
	_args:Tuple[Any, ...], _kwargs:Dict[str, Any], datetime:Any=datetime) -> str:
		args:Tuple[Any, ...] = tuple(map(lambda v: v() if callable(v) else v, _args))
		kwargs:Dict[str, Any] = dict(map(lambda d: (d[0], (d[1]() if callable(d[1]) else d[1])), _kwargs.items()))
		return self.messageFormat.format(
			levelnumber=levelID,
			levelname=Levels.getLevelNameByID(levelID),
			levelshortname=Levels.getLevelShortNameByID(levelID),
			date=datetime.utcfromtimestamp(timestamp).strftime(self.dateFormat),
			timestamp=timestamp,
			ellapsed=timestamp - self.delta,
			message=message.format(*args, **kwargs) if args or kwargs else message,
			name=name
		)
	def initStandardOutStream(self) -> None:
		self.modules.append( STDOutStreamingModule(self._stdout) )
		return None
	def initFileStream(self, fullPath:str) -> None:
		self.modules.append( FileStream(fullPath) )
		return None
	def initRotatedFileStream(self, fullPath:str, maxBytes:int=0, rotateDaily:bool=False, maxBackup:Optional[int]=None) -> None:
		self.modules.append( RotatedFileStream(fullPath, maxBytes, rotateDaily, maxBackup) )
		return None
	def initDailyFileStream(self, logPath:str, prefix:str, postfix:str, dateFormat:str="%Y-%m-%d") -> None:
		self.modules.append( DailyFileStream(logPath, prefix, postfix, dateFormat) )
		return None

class DowngradedLoggerManager(LoggerManager):
	def __init__(self) -> None:
		LoggerManager.handler = self
		if "logging" not in globals():
			import logging
		self.logging = logging
	def _emit(self, name:str, levelID:int, timestamp:float, message:Any, _args:Tuple[Any, ...], _kwargs:Dict[str, Any]) -> None:
		args:Tuple[Any, ...] = tuple(map(lambda v: v() if callable(v) else v, _args))
		kwargs:Dict[str, Any] = dict(map(lambda d: (d[0], (d[1]() if callable(d[1]) else d[1])), _kwargs.items()))
		self.logging.getLogger(name).log(
			self.logging._nameToLevel.get({
				"CRITICAL":"CRITICAL",
				"ERROR":"ERROR",
				"WARNING":"WARNING",
				"INFO":"INFO",
				"DEBUG":"DEBUG",
				"TRACE":"DEBUG",
			}.get(Levels.getLevelNameByID(levelID), "NOTSET"), 0),
			message.format(*args, **kwargs) if args or kwargs else message
		)
		return None
	def _getFilterData(self, name:str) -> Tuple[float, int]:
		return time(), 0

# Finalizing imports
from .modules import (STDOutStreamingModule, ModuleBase, STDErrModule, STDOutModule, FileStream, RotatedFileStream,
DailyFileStream)
from .levels import Levels
from .filters import Filter, FilterParser
from .logger import Logger
