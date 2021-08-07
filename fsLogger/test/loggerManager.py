# Builtin modules
from __future__ import annotations
import unittest
from typing import List
from tempfile import TemporaryDirectory
# Third party modules
# Local modules
from .. import LoggerManager, Logger
from ..abcs import T_ModuleBase
# Program

class CaptureModule(T_ModuleBase):
	data:List[str]
	def __init__(self) -> None:
		self.data = []
	def emit(self, data:str) -> None:
		self.data.append(data)
	def close(self) -> None:
		self.data.clear()

class LoggerManagerTest(unittest.TestCase):
	def test(self) -> None:
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
			fn = "{}/teszt.log".format(tmpdir)
			lm.initFileStream(fn)
			log.info("Hello")
			with open(fn, "rt") as fid:
				self.assertEqual(fid.read(), "[INF][test] : Hello\n")
		lm.close()
		lm = LoggerManager(
			messageFormat="[{levelshortname}][{name}] : {message}\n",
			defaultLevel="TRACE",
			hookSTDOut=True,
			hookSTDErr=False
		)
		with TemporaryDirectory() as tmpdir:
			fn = "{}/teszt.log".format(tmpdir)
			lm.initFileStream(fn)
			print("Hel", end="")
			print("lo")
			print("Hello")
			with open(fn, "rt") as fid:
				self.assertEqual(fid.read(), "[INF][Standard.Output] : Hello\n[INF][Standard.Output] : Hello\n")
		lm.close()
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
		#
		lm = LoggerManager(
			"Client:WARNING,Server:DISABLED,Server.Important:TRACE",
			messageFormat="{message}",
			defaultLevel="DEBUG",
			hookSTDOut=False,
			hookSTDErr=False
		)
		mod = CaptureModule()
		lm.modules.append( mod )
		for lName, lvl, s in (
			("client", "trace", False),
			("client", "debug", False),
			("client", "info", False),
			("client", "warning", True),
			("client", "error", True),
			("client", "critical", True),
			("client.sql", "trace", False),
			("client.sql", "debug", False),
			("client.sql", "info", False),
			("client.sql", "warning", True),
			("client.sql", "error", True),
			("client.sql", "critical", True),
			("Client", "trace", False),
			("Client", "debug", False),
			("Client", "info", False),
			("Client", "warning", True),
			("Client", "error", True),
			("Client", "critical", True),
			("Client.sql", "trace", False),
			("Client.sql", "debug", False),
			("Client.sql", "info", False),
			("Client.sql", "warning", True),
			("Client.sql", "error", True),
			("Client.sql", "critical", True),
			("Server", "trace", False),
			("Server", "debug", False),
			("Server", "info", False),
			("Server", "warning", False),
			("Server", "error", False),
			("Server", "critical", False),
			("Server.Something", "trace", False),
			("Server.Something", "debug", False),
			("Server.Something", "info", False),
			("Server.Something", "warning", False),
			("Server.Something", "error", False),
			("Server.Something", "critical", False),
			("Something", "trace", False),
			("Something", "debug", True),
			("Something", "info", True),
			("Something", "warning", True),
			("Something", "error", True),
			("Something", "critical", True),
			("Server.Important", "trace", True),
			("Server.Important", "debug", True),
			("Server.Important", "info", True),
			("Server.Important", "warning", True),
			("Server.Important", "error", True),
			("Server.Important", "critical", True),
		):
			getattr(Logger(lName), lvl)("ok")
			self.assertListEqual(mod.data, ["ok"] if s else [])
			mod.close()
		return None
