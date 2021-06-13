__version__ = "0.0.2"
__doc__ = """
Logging utility v{}
Copyright (C) 2021 Fusion Solutions KFT <contact@fusionsolutions.io>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/lgpl.txt>.
""".format(__version__)
from typing import Union, Optional
from .levels import Levels
from .filters import Filter, FilterParser
from .logger import Logger
from .loggerManager import LoggerManager, DowngradedLoggerManager

root:Optional[LoggerManager] = None
def SimpleLogger(level:Union[str, int]="TRACE") -> LoggerManager:
	global root
	root = LoggerManager(defaultLevel=level)
	root.initStandardOutStream()
	return root

def downgradeLoggerManager() -> LoggerManager:
	global root
	root = DowngradedLoggerManager()
	return root

__all__ = "LoggerManager", "Logger", "Levels", "FilterParser", "SimpleLogger", "downgradeLoggerManager"
