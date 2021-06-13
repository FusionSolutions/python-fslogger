# Builtin modules
from __future__ import annotations
import logging, unittest
# Local modules
from .filters import FilterTest
from .levels import LevelsTest
from .loggerManager import LoggerManagerTest
# Program
logging.basicConfig(format='[%(levelname).3s][%(asctime)s][%(name)s]: %(message)s', level=logging.INFO)
unittest.main(verbosity=2)
