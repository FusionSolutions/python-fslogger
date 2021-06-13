# Builtin modules
from __future__ import annotations
import json, re, unittest
from fnmatch import fnmatchcase
from typing import Dict, List, Any, Union, Tuple, Optional, cast
from collections import OrderedDict
# Local modules
from . import Levels
# Program
class Filter:
	__slots__ = "keys", "fallbackLevel",
	def __init__(self, fallbackLevel:int):
		self.keys:Dict[str, Filter] = cast(Dict[str, Filter], OrderedDict())
		self.fallbackLevel = fallbackLevel
	def addLogger(self, k:str, v:Filter) -> Filter:
		self.keys[k] = v
		return self
	def setFallbackLevel(self, level:Union[int, str]):
		self.fallbackLevel = Levels.parse(level)
	def getKey(self, k:str) -> Optional[Filter]:
		if k.lower() in self.keys:
			return self.keys[k.lower()]
		return None
	def getFilteredID(self, path:List[str]) -> int:
		name:str = path.pop(0)
		key:str
		val:Filter
		for key, val in reversed(self.keys.items()):
			if name == key or fnmatchcase(name, key):
				if path:
					return val.getFilteredID(path) or self.fallbackLevel
				else:
					return val.fallbackLevel or self.fallbackLevel
		return self.fallbackLevel
	def dump(self) -> list:
		ret:list = [{ "*":self.fallbackLevel }]
		key:str
		val:Filter
		for key, val in self.keys.items():
			ret.append({ key:val.dump() })
		return ret
	def extend(self, inp:Filter) -> None:
		key:str
		val:Union[int, Filter]
		if inp.fallbackLevel != 0:
			self.fallbackLevel = inp.fallbackLevel
		for key, val in inp.keys.items():
			if key == "*":
				self.fallbackLevel = cast(int, val)
			else:
				if key not in self.keys:
					self.keys[key] = Filter(0)
				self.keys[key].extend(cast(Filter, val))

class FilterParser:
	@classmethod
	def fromString(self, data:str) -> Filter:
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
		paths:List[str]
		rawPaths:str
		levelID:str
		lastScope:Filter
		ret:Filter = Filter(0)
		i:int
		for part in data.lower().split(","):
			rawPaths, levelID = part.split(":")
			paths = rawPaths.split(LoggerManager.groupSeperator)
			lastScope = ret
			for i, path in enumerate(paths):
				if path not in lastScope.keys:
					lastScope.keys[path] = Filter(Levels.parse(levelID) if i == len(paths)-1 else 0)
				lastScope = lastScope.keys[path]
		return ret
	@classmethod
	def fromJson(self, datas:list) -> Filter:
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
		data:Dict[str, Any]
		ret:Filter = Filter(0)
		for data in datas:
			for key in data.keys():
				if isinstance(data[key], list):
					ret.keys[key] = self.fromJson(data[key])
				elif key == "*":
					ret.fallbackLevel = Levels.parse(data[key])
				else:
					# Fallback for lazy input
					ret.keys[key.lower()] = self.fromJson([ {"*": Levels.parse(data[key])} ])
		return ret

class FilterTest(unittest.TestCase):
	def test(self):
		LoggerManager.groupSeperator = "-"
		beforeFilterData:list = [
			{ "server": [
				{ "client": [
					{ "*": 50 },
					{ "192.168.*": [
						{ "*": 40 },
					]},
					{ "192.168.1.*": [
						{ "*": 40 },
					]},
					{ "192.168.2.*": [
						{ "*": 20 },
						{ "sql": [
							{ "*": 40 },
						]},
					]},
					{ "192.168.2.1": [
						{ "*": 10 }
					]}
				]}
			]}
		]
		afterFilterData:list = [
			{ "*": 0 },
			{ "server": [
				{ "*": 0 },
				{ "client": [
					{ "*": 50 },
					{ "192.168.*": [
						{ "*": 40 },
					]},
					{ "192.168.1.*": [
						{ "*": 40 },
					]},
					{ "192.168.2.*": [
						{ "*": 20 },
						{ "sql": [
							{ "*": 40 },
						]},
					]},
					{ "192.168.2.1": [
						{ "*": 10 }
					]}
				]}
			]}
		]
		filter:Filter = FilterParser.fromJson(beforeFilterData)
		self.assertEqual( filter.dump(), afterFilterData )
		self.assertEqual( filter.getFilteredID(["some"]), 0)
		self.assertEqual( filter.getFilteredID(["server"]), 0 )
		self.assertEqual( filter.getFilteredID(["server", "client"]), 50 )
		self.assertEqual( filter.getFilteredID(["server", "client", "255.255.255.255"]), 50 )
		self.assertEqual( filter.getFilteredID(["server", "client", "255.255.255.255", "sql"]), 50 )
		self.assertEqual( filter.getFilteredID(["server", "client", "192.168.0.0"]), 40 )
		self.assertEqual( filter.getFilteredID(["server", "client", "192.168.1.0"]), 40 )
		self.assertEqual( filter.getFilteredID(["server", "client", "192.168.1.2"]), 40 )
		self.assertEqual( filter.getFilteredID(["server", "client", "192.168.1.2", "sql"]), 40 )
		self.assertEqual( filter.getFilteredID(["server", "client", "192.168.2.0"]), 20 )
		self.assertEqual( filter.getFilteredID(["server", "client", "192.168.2.0", "result"]), 20 )
		self.assertEqual( filter.getFilteredID(["server", "client", "192.168.2.0", "sql"]), 40 )
		self.assertEqual( filter.getFilteredID(["server", "client", "192.168.2.0", "sql", "execute"]), 40 )
		self.assertEqual( filter.getFilteredID(["server", "client", "192.168.2.1", "sql"]), 10 )
		self.assertEqual( filter.getFilteredID(["server", "client", "192.168.2.1", "sql", "execute"]), 10 )
		self.assertEqual( filter.getFilteredID(["server", "client", "192.168.2.3", "sql", "execute"]), 40 )
		self.assertEqual( filter.getFilteredID(["server", "client", "192.168.2.3", "somewhat"]), 20 )
		filter.extend( FilterParser.fromString("server:50,server-client-192.168.2.*:50,server-client-192.168.2.4-sql:50") )
		self.assertEqual( filter.getFilteredID(["server"]), 50 )
		self.assertEqual( filter.getFilteredID(["server", "client"]), 50 )
		self.assertEqual( filter.getFilteredID(["server", "client", "255.255.255.255"]), 50 )
		self.assertEqual( filter.getFilteredID(["server", "client", "255.255.255.255", "sql"]), 50 )
		self.assertEqual( filter.getFilteredID(["server", "client", "192.168.0.0"]), 40 )
		self.assertEqual( filter.getFilteredID(["server", "client", "192.168.1.0"]), 40 )
		self.assertEqual( filter.getFilteredID(["server", "client", "192.168.1.2"]), 40 )
		self.assertEqual( filter.getFilteredID(["server", "client", "192.168.1.2", "sql"]), 40 )
		self.assertEqual( filter.getFilteredID(["server", "client", "192.168.2.0"]), 50 )
		self.assertEqual( filter.getFilteredID(["server", "client", "192.168.2.0", "result"]), 50 )
		self.assertEqual( filter.getFilteredID(["server", "client", "192.168.2.0", "sql"]), 40 )
		self.assertEqual( filter.getFilteredID(["server", "client", "192.168.2.0", "sql", "execute"]), 40 )
		self.assertEqual( filter.getFilteredID(["server", "client", "192.168.2.1", "sql"]), 10 )
		self.assertEqual( filter.getFilteredID(["server", "client", "192.168.2.1", "sql", "execute"]), 10 )
		self.assertEqual( filter.getFilteredID(["server", "client", "192.168.2.3", "sql", "execute"]), 40 )
		self.assertEqual( filter.getFilteredID(["server", "client", "192.168.2.3", "somewhat"]), 50 )
		self.assertEqual( filter.getFilteredID(["server", "client", "192.168.2.4"]), 50 )
		self.assertEqual( filter.getFilteredID(["server", "client", "192.168.2.4", "somewhat"]), 50 )

from .loggerManager import LoggerManager
