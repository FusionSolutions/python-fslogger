# Builtin modules
from __future__ import annotations
from typing import Tuple, Any, Dict, Optional
# Third party modules
# Local modules
from .abcs import T_LoggerManager
# Program
class _GlobHandler:
	handler:Optional[T_LoggerManager] = None
	@classmethod
	def close(cls) -> None:
		if isinstance(cls.handler, T_LoggerManager):
			cls.handler.close()
		return None
	@classmethod
	def isActive(cls) -> bool:
		return isinstance(cls.handler, T_LoggerManager)
	@classmethod
	def activate(cls, l:T_LoggerManager) -> None:
		if cls.isActive():
			raise RuntimeError("LoggerManager already initialized")
		cls.handler = l
		return None
	@classmethod
	def get(cls) -> Optional[T_LoggerManager]:
		return cls.handler
	@classmethod
	def clear(cls) -> None:
		cls.handler = None
	@classmethod
	def getGroupSeperator(cls) -> str:
		if isinstance(cls.handler, T_LoggerManager):
			return cls.handler.groupSeperator
		return "."
	@classmethod
	def setGroupSeperator(cls, groupSeparator:str) -> None:
		if isinstance(cls.handler, T_LoggerManager):
			cls.handler.groupSeperator = groupSeparator
		return None
	@classmethod
	def getFilterChangeTime(cls) -> float:
		if isinstance(cls.handler, T_LoggerManager):
			return cls.handler.filterChangeTime
		return 0.0
	@classmethod
	def emit(cls, name:str, levelID:int, timestamp:float, message:Any, _args:Tuple[Any, ...], _kwargs:Dict[str, Any]) -> None:
		if isinstance(cls.handler, T_LoggerManager):
			cls.handler.emit(name, levelID, timestamp, message, _args, _kwargs)
		return None
	@classmethod
	def getFilterData(cls, name:str) -> Tuple[float, int]:
		if isinstance(cls.handler, T_LoggerManager):
			return cls.handler.getFilterData(name)
		return 0.0, 0
