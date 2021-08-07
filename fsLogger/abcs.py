# Builtin modules
from __future__ import annotations
from abc import ABCMeta, abstractmethod
from threading import RLock
# from socket import socket
from typing import Dict, Tuple, Optional, Any, List
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
	def close(self, ) -> None: ...
	@abstractmethod
	def emit(self, name:str, levelID:int, timestamp:float, message:Any, _args:Tuple[Any, ...], _kwargs:Dict[str, Any]) -> None: ...
	@abstractmethod
	def getFilterData(self, name:str) -> Tuple[float, int]: ...
	
class T_ModuleBase(metaclass=ABCMeta):
	@abstractmethod
	def emit(self, data:str) -> None: pass
	@abstractmethod
	def close(self) -> None: pass
