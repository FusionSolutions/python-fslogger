# Builtin modules
import unittest
# Third party modules
# Local modules
from .. import Levels
# Program
class LevelsTest(unittest.TestCase):
	def test_parser(self) -> None:
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
		Levels.removeLevel("LOWLEVEL")
		return None
	def test_gets(self) -> None:
		self.assertEqual( Levels.getLevelNameByID(40), "WARNING" )
		self.assertEqual( Levels.getLevelShortNameByID(40), "WAR" )
		with self.assertRaises(KeyError):
			Levels.getLevelNameByID(15)
		with self.assertRaises(KeyError):
			Levels.getLevelShortNameByID(15)
		return None
