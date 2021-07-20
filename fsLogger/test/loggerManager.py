# Builtin modules
import unittest
from tempfile import TemporaryDirectory
# Third party modules
# Local modules
from .. import LoggerManager, Logger
# Program
class LoggerManagerTest(unittest.TestCase):
	def test_first(self) -> None:
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
		lm.close()
		return None
	def test_second(self) -> None:
		lm = LoggerManager(
			messageFormat="[{levelshortname}][{name}] : {message}\n",
			defaultLevel="TRACE",
			hookSTDOut=True,
			hookSTDErr=False
		)
		with TemporaryDirectory() as tmpdir:
			fn:str = "{}/teszt.log".format(tmpdir)
			lm.initFileStream(fn)
			print("Hel", end="")
			print("lo")
			print("Hello")
			with open(fn, "rt") as fid:
				self.assertEqual(fid.read(), "[INF][Standard.Output] : Hello\n[INF][Standard.Output] : Hello\n")
		lm.close()
		return None
	def test_third(self) -> None:
		lm = LoggerManager(
			messageFormat="[{levelshortname}][{name}] : {message}\n",
			defaultLevel="TRACE",
			hookSTDOut=True,
			hookSTDErr=False
		)
		lm.initStandardOutStream()
		log = Logger("test")
		log.info("Format test {} {:x}", "test", 88)
		lm.close()
		return None
