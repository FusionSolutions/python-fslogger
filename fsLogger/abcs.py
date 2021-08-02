# Builtin modules
from __future__ import annotations
from abc import ABCMeta, abstractmethod
from threading import RLock
# from socket import socket
from typing import Dict, Tuple, Optional, Any, Union, List
# Third party modules
# Local modules
# Program
class T_LoggerManager(metaclass=ABCMeta):
	lock:RLock
	handler:Optional[T_LoggerManager]
	filterChangeTime:float
	groupSeperator:str
	modules:List[T_ModuleBase]
	@abstractmethod
	def __init__(self, filter:Optional[Union[List[Any], str, T_Filter]]=..., messageFormat:str=..., dateFormat:str=...,
	defaultLevel:Optional[Union[int, str]]=..., hookSTDOut:bool=..., hookSTDErr:bool=...): ...
	@abstractmethod
	def close(self, ) -> None: ...
	@abstractmethod
	def emit(self, name:str, levelID:int, timestamp:float, message:Any, _args:Tuple[Any, ...], _kwargs:Dict[str, Any]) -> None: ...
	@abstractmethod
	def extendFilter(self, data:Union[List[Any], str, T_Filter]) -> None: ...
	@abstractmethod
	def getFilterData(self, name:str) -> Tuple[float, int]: ...

class T_Logger(metaclass=ABCMeta):
	name:str
	filterChangeTime:float
	lastFilterLevel:int
	@abstractmethod
	def getChild(self, name:str) -> T_Logger: ...
	@abstractmethod
	def isFiltered(self, levelID:Union[int, str]) -> bool: ...
	@abstractmethod
	def trace(self, message:str, *args:Any, **kwargs:Any) -> None: ...
	@abstractmethod
	def debug(self, message:str, *args:Any, **kwargs:Any) -> None: ...
	@abstractmethod
	def info(self, message:str, *args:Any, **kwargs:Any) -> None: ...
	@abstractmethod
	def warn(self, message:str, *args:Any, **kwargs:Any) -> None: ...
	@abstractmethod
	def warning(self, message:str, *args:Any, **kwargs:Any) -> None: ...
	@abstractmethod
	def error(self, message:str, *args:Any, **kwargs:Any) -> None: ...
	@abstractmethod
	def critical(self, message:str, *args:Any, **kwargs:Any) -> None: ...
	@abstractmethod
	def fatal(self, message:str, *args:Any, **kwargs:Any) -> None: ...
	
class T_Filter(metaclass=ABCMeta):
	keys:Dict[str, T_Filter]
	fallbackLevel:int
	@abstractmethod
	def __init__(self, fallbackLevel:int) -> None: ...
	@abstractmethod
	def addLogger(self, k:str, v:T_Filter) -> T_Filter: ...
	@abstractmethod
	def setFallbackLevel(self, level:Union[int, str]) -> None: ...
	@abstractmethod
	def getKey(self, k:str) -> Optional[T_Filter]: ...
	@abstractmethod
	def getFilteredID(self, path:List[str]) -> int: ...
	@abstractmethod
	def dump(self) -> List[Any]: ...
	@abstractmethod
	def extend(self, inp:T_Filter) -> None: ...
	
class T_ModuleBase(metaclass=ABCMeta):
	@abstractmethod
	def emit(self, data:str) -> None: pass
	@abstractmethod
	def close(self) -> None: pass
