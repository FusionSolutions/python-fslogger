# Builtin modules
from __future__ import annotations
import sys, atexit, traceback
from datetime import datetime
from time import monotonic
from threading import RLock
from typing import Dict, List, Any, cast, TextIO, Union, Tuple, Optional
# Third party modules
# Local modules
from .globHandler import _GlobHandler
from .abcs import T_LoggerManager
from .filter import Filter, FilterParser
from .modules import STDOutStreamingModule, STDErrModule, STDOutModule, FileStream, RotatedFileStream, DailyFileStream
from .levels import Levels
# Program
DEF_LEVEL = "WARNING"
DEF_FORMAT = "[{levelshortname}][{date}][{name}] : {message}\n"
DEF_DATE = "%Y-%m-%d %H:%M:%S.%f"

class LoggerManager(T_LoggerManager):
	lock = RLock()
	filterChangeTime = monotonic()
	groupSeperator = "."
	@staticmethod
	def getHandler() -> Optional[T_LoggerManager]:
		return _GlobHandler.get()
	def __init__(self, filter:Optional[Union[List[Any], str, Filter]]=None, messageFormat:str=DEF_FORMAT,
	dateFormat:str=DEF_DATE, defaultLevel:Optional[Union[int, str]]=None, hookSTDOut:bool=True, hookSTDErr:bool=True):
		_GlobHandler.activate(self)
		self.filter        = Filter(Levels.parse(DEF_LEVEL if defaultLevel is None else defaultLevel ))
		if filter is not None:
			self.extendFilter(filter)
		self.delta         = monotonic()
		self.messageFormat = messageFormat
		self.dateFormat    = dateFormat
		self.modules       = []
		self._stderr       = sys.stderr
		self._stdout       = sys.stdout
		self._excepthook   = sys.excepthook
		if hookSTDErr:
			sys.stderr     = cast(TextIO, STDErrModule())
			sys.excepthook = lambda *a: sys.stderr.write("".join(traceback.format_exception(*a)))
		if hookSTDOut:
			sys.stdout = cast(TextIO, STDOutModule())
		atexit.register(self.close)
	def __del__(self) -> None:
		self.close()
		return None
	def getFilterData(self, name:str) -> Tuple[float, int]:
		return (
			self.filterChangeTime,
			self.filter.getFilteredID(
				name.lower().split(self.groupSeperator)
			)
		)
	def emit(self, name:str, levelID:int, timestamp:float, message:Any, _args:Tuple[Any, ...], _kwargs:Dict[str, Any]) -> None:
		parsedMessage = self.messageFormatter(name, levelID, timestamp, message, _args, _kwargs)
		with self.lock:
			for handler in self.modules:
				try: handler.emit(parsedMessage)
				except: pass
	def extendFilter(self, data:Union[List[Any], str, Filter]) -> None:
		filter = Filter(0)
		if isinstance(data, list):
			filter = FilterParser.fromJson(data)
		elif isinstance(data, str):
			filter = FilterParser.fromString(data)
		assert isinstance(filter, Filter)
		self.filter.extend(filter)
	def close(self) -> None:
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
		_GlobHandler.clear()
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
		_GlobHandler.activate(self)
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
		return monotonic(), 0
