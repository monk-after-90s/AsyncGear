import asyncUnittest
from Gear_test import TestGear
from method_run_when_test import TestClass_run_when
from run_when_test import TestRunWhen
from DataShine_test import TestDataShine
from loguru import logger
import sys

logger.remove()
logger.add(sys.stderr, level="INFO")
asyncUnittest.run()
from Gear_test_no_create_task import asyncUnittest

asyncUnittest.run()
# 测试通过不了的话就分别测试
