# Builtin modules
import unittest
from typing import List, Any
# Third party modules
# Local modules
from .. import LoggerManager, FilterParser
from ..globHandler import _GlobHandler
# Program
class FilterTest(unittest.TestCase):
	def test(self) -> None:
		lm = LoggerManager(
			messageFormat="[{levelshortname}][{name}] : {message}\n",
			defaultLevel="TRACE",
			hookSTDOut=False,
			hookSTDErr=False
		)
		_old = _GlobHandler.getGroupSeperator()
		_GlobHandler.setGroupSeperator("-")
		beforeFilterData:List[Any] = [
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
		afterFilterData:List[Any] = [
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
		filter = FilterParser.fromJson(beforeFilterData)
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
		_GlobHandler.setGroupSeperator(_old)
		lm.close()
		return None
