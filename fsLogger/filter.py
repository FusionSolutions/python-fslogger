# Builtin modules
from __future__ import annotations
from fnmatch import fnmatchcase
from typing import Dict, List, Any, Union, Optional, cast
from collections import OrderedDict
# Third party modules
# Local modules
from .globHandler import _GlobHandler
from .levels import Levels
# Program
class Filter:
	keys:Dict[str, Filter]
	fallbackLevel:int
	__slots__ = ("keys", "fallbackLevel")
	def __init__(self, fallbackLevel:int) -> None:
		self.keys          = cast(Dict[str, Filter], OrderedDict())
		self.fallbackLevel = fallbackLevel
	def addLogger(self, k:str, v:Filter) -> Filter:
		self.keys[k] = v
		return self
	def setFallbackLevel(self, level:Union[int, str]) -> None:
		self.fallbackLevel = Levels.parse(level)
		return None
	def getKey(self, k:str) -> Optional[Filter]:
		return self.keys[k.lower()] if k.lower() in self.keys else None
	def getFilteredID(self, path:List[str]) -> int:
		name = path.pop(0)
		for key, val in reversed(list(self.keys.items())):
			if name == key or fnmatchcase(name, key):
				if path:
					return val.getFilteredID(path) or self.fallbackLevel
				else:
					return val.fallbackLevel or self.fallbackLevel
		return self.fallbackLevel
	def dump(self) -> List[Any]:
		ret:List[Any] = [{ "*":self.fallbackLevel }]
		for key, val in self.keys.items():
			ret.append({ key:val.dump() })
		return ret
	def extend(self, inp:Filter) -> None:
		if inp.fallbackLevel != 0:
			self.fallbackLevel = inp.fallbackLevel
		for key, val in inp.keys.items():
			if key == "*":
				self.fallbackLevel = cast(int, val)
			else:
				if key not in self.keys:
					self.keys[key] = Filter(0)
				self.keys[key].extend(val)
		return None

class FilterParser:
	@staticmethod
	def fromString(data:str) -> Filter:
		"""
		parent:ERROR,parent.children.son:WARNING
		->
		[
			{ "*": 0 },
			{ "parent": [
				{ "*": 50 },
				{ "children": [
					{ "*": 0 },
					{ "son": [
						{ "*": 40 }
					]}
				]}
			]}
		]
		"""
		lastScope:Filter
		ret = Filter(0)
		for part in data.lower().split(","):
			rawPaths, levelID = part.split(":")
			paths = rawPaths.split(_GlobHandler.getGroupSeperator())
			lastScope = ret
			for i, path in enumerate(paths):
				if path not in lastScope.keys:
					lastScope.keys[path] = Filter(Levels.parse(levelID) if i == len(paths)-1 else 0)
				lastScope = lastScope.keys[path]
		return ret
	@classmethod
	def fromJson(cls, datas:List[Any]) -> Filter:
		"""
		[
			{ "parent": [
				{ "*": 50 },
				{ "children": [
					{ "son": [
						{ "*": 40 }
					]}
				]}
			]}
		]
		->
		[
			{ "*": 0 },
			{ "parent": [
				{ "*": 50 },
				{ "children": [
					{ "*": 0 },
					{ "son": [
						{ "*": 40 }
					]}
				]}
			]}
		]
		"""
		ret = Filter(0)
		for data in datas:
			for key in data.keys():
				if isinstance(data[key], list):
					ret.keys[key.lower()] = cls.fromJson(data[key])
				elif key == "*":
					ret.fallbackLevel = Levels.parse(data[key])
				else:
					# Fallback for lazy input
					ret.keys[key.lower()] = cls.fromJson([ {"*": Levels.parse(data[key])} ])
		return ret

