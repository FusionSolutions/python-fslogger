# Builtin modules
from __future__ import annotations
import unittest
from typing import List, Union, Tuple
# Local modules
# Program
class Levels:
	levels:List[ Tuple[int, str, str] ] = [
		(100, "DISABLED", "DIS"),
		(60, "CRITICAL", "CRI"),
		(50, "ERROR", "ERR"),
		(40, "WARNING", "WAR"),
		(30, "INFO", "INF"),
		(20, "DEBUG", "DBG"),
		(10, "TRACE", "TRC"),
	]
	@classmethod
	def addLevel(self, id:int, name:str, shortName:str):
		assert id > 0, "ID must be higher as zero"
		self.levels.append((id, name, shortName))
		self.levels = sorted(self.levels, key=lambda x: -x[0])
	@classmethod
	def getLevelIDByName(self, name:str) -> int:
		name = name.upper()
		d:Tuple[int, str, str]
		for d in self.levels:
			if d[1] == name:
				return d[0]
		return 0
	@classmethod
	def getLevelIDByShortName(self, shortName:str) -> int:
		shortName = shortName.upper()
		d:Tuple[int, str, str]
		for d in self.levels:
			if d[2] == shortName:
				return d[0]
		return 0
	@classmethod
	def getLevelNameByID(self, id:int) -> str:
		d:Tuple[int, str, str]
		for d in self.levels:
			if d[0] == id:
				return d[1]
		raise KeyError("Levels: Unknown level: {}".format(id))
	@classmethod
	def getLevelShortNameByID(self, id:int) -> str:
		d:Tuple[int, str, str]
		for d in self.levels:
			if d[0] == id:
				return d[2]
		raise KeyError("Levels: Unknown level: {}".format(id))
	@classmethod
	def parse(self, level:Union[int, str]) -> int:
		r:int
		if isinstance(level, str) and level.isdigit():
			level = int(level)
		if isinstance(level, int):
			for d in self.levels:
				if d[0] == level:
					return level
		else:
			r = self.getLevelIDByName(level)
			if r == 0:
				r = self.getLevelIDByShortName(level)
			if r != 0:
				return r
		raise KeyError("Levels: Unknown level: {}".format(level))

class LevelsTest(unittest.TestCase):
	def test_parser(self):
		self.assertEqual( Levels.parse("DISAbLED"), 100 )
		self.assertEqual( Levels.parse("WARnING"), 40 )
		self.assertEqual( Levels.parse("wAr"), 40 )
		with self.assertRaises(KeyError):
			Levels.parse("NOTHING")
		with self.assertRaises(KeyError):
			Levels.parse(5)
		Levels.addLevel(5, "LOWLEVEL", "LOW")
		self.assertEqual( Levels.parse("LOWLEVEL"), 5 )
		self.assertEqual( Levels.parse("LOW"), 5 )
		self.assertEqual( Levels.parse(5), 5 )
	def test_gets(self):
		self.assertEqual( Levels.getLevelNameByID(40), "WARNING" )
		self.assertEqual( Levels.getLevelShortNameByID(40), "WAR" )
		with self.assertRaises(KeyError):
			Levels.getLevelNameByID(15)
		with self.assertRaises(KeyError):
			Levels.getLevelShortNameByID(15)
