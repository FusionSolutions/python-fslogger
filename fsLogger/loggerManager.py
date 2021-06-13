# Builtin modules
from __future__ import annotations
import sys, atexit, traceback, unittest
from datetime import datetime
from time import monotonic
from threading import RLock
from typing import Dict, List, Any, cast, TextIO, Union, Iterable, Tuple, Optional, Callable
# Local modules
# Program
DEF_FILTER:List[Dict[str, Any]] = [{ "*":"TRACE" }]
DEF_FORMAT:str = "[{levelshortname}][{date}][{name}] : {message}\n"
DEF_DATE:str = "%Y-%m-%d %H:%M:%S.%f"

class LoggerManager:
	lock:RLock = RLock()
	handler:Optional[LoggerManager] = None
	filterChangeTime:float = monotonic()
	groupSeperator:str = "."
	def __init__(self, filter:Union[list, str, Filter]=DEF_FILTER, messageFormat:str=DEF_FORMAT, dateFormat:str=DEF_DATE,
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
	def _emit(self, name:str, levelID:int, timestamp:float, message:Any, _args:Tuple[Any, ...], _kwargs:Dict[str, Any]) -> None:
		parsedMessage:str = self.messageFormatter(name, levelID, timestamp, message, _args, _kwargs)
		with self.lock:
			for handler in self.modules:
				try: handler.emit(parsedMessage)
				except: pass
	@staticmethod
	def extendFilter(data:Union[list, str, Filter]) -> None:
		if isinstance(LoggerManager.handler, LoggerManager):
			LoggerManager.handler._extendFilter(data)
	def _extendFilter(self, data:Union[list, str, Filter]) -> None:
		filter:Filter = Filter(0)
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
	def _close(self) -> None:
		module:ModuleBase
		for module in self.modules:
			try:
				module.close()
			except:
				pass
		self.modules.clear()
		LoggerManager.handler = None
	@staticmethod
	def getLogger(self, name:str) -> "Logger":
		return Logger(name)
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
	def initFileStream(self, fullPath:str) -> None:
		self.modules.append( FileStream(fullPath) )
	def initRotatedFileStream(self, fullPath:str, maxBytes:int=0, rotateDaily:bool=False, maxBackup:Optional[int]=None) -> None:
		self.modules.append( RotatedFileStream(fullPath, maxBytes, rotateDaily, maxBackup) )
	def initDailyFileStream(self, logPath:str, prefix:str, postfix:str, dateFormat:str="%Y-%m-%d") -> None:
		self.modules.append( DailyFileStream(logPath, prefix, postfix, dateFormat) )

class DowngradedLoggerManager(LoggerManager):
	import logging
	def __init__(self):
		LoggerManager.handler = self
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
	def _getFilterData(self, name:str) -> Tuple[float, int]:
		return time(), 0

class LoggerManagerTest(unittest.TestCase):
	def test(self):
		from tempfile import TemporaryDirectory
		lm = LoggerManager(
			messageFormat="[{levelshortname}][{name}] : {message}\n",
			defaultLevel="TRACE",
			hookSTDOut=False,
			hookSTDErr=False
		)
		log = Logger("test")
		lm.initStandardOutStream()
		log.info("If you see this i'm working well")
		with TemporaryDirectory() as tmpdir:
			fn:str = "{}/teszt.log".format(tmpdir)
			lm.initFileStream(fn)
			log.info("Hello")
			with open(fn, "rt") as fid:
				self.assertEqual(fid.read(), "[INF][test] : Hello\n")

# Finalizing imports
from .modules import *
from .levels import Levels
from .filters import Filter, FilterParser
from .logger import Logger
