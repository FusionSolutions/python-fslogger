from __future__ import annotations
__version__ = "0.1.3"
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
# Builtin modules
from typing import Union, cast
# Third party modules
# Local modules
from .globHandler import _GlobHandler
from .levels import Levels
from .filter import Filter, FilterParser
from .logger import Logger
from .loggerManager import LoggerManager, DowngradedLoggerManager
from .abcs import T_LoggerManager
# Program
def SimpleLogger(level:Union[str, int]="TRACE") -> T_LoggerManager:
	lm:T_LoggerManager
	if not _GlobHandler.isActive():
		lm = LoggerManager(defaultLevel=level)
		lm.initStandardOutStream()
	else:
		lm = cast(T_LoggerManager, _GlobHandler.get())
	return lm

def downgradeLoggerManager() -> T_LoggerManager:
	lm:T_LoggerManager
	if not _GlobHandler.isActive():
		lm = DowngradedLoggerManager()
	else:
		lm = cast(T_LoggerManager, _GlobHandler.get())
	return lm

__all__ = "LoggerManager", "Logger", "Levels", "Filter", "FilterParser", "SimpleLogger", "downgradeLoggerManager"
