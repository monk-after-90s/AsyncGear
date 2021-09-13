import asyncUnittest
from Gear_test import TestGear
from method_run_when_test import TestInstance_run_when
from run_when_test import TestRunWhen
from DataShine_test import TestDataShine
from loguru import logger
import sys

logger.remove()
logger.add(sys.stderr, level="INFO")
asyncUnittest.run()
