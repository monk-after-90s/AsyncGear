import asyncio

from asyncUnittest import AsyncTestCase
import asyncUnittest

from AsyncExclusivePeriods import AsyncExclusivePeriod


class TestAsyncExclusivePeriod(AsyncTestCase):
    async def setUp(self) -> None:
        await AsyncExclusivePeriod.create_obj_periods(self, 'test1', 'test2', 'test3')
        self.assertEqual(AsyncExclusivePeriod.get_obj_present_period(self), 'test1')

    async def test_add_period(self):
        await AsyncExclusivePeriod.add_period(self, 'test4')
        self.assertEqual(AsyncExclusivePeriod.get_obj_present_period(self), 'test1')
        obj_period_names = AsyncExclusivePeriod.get_obj_period_names(self)
        self.assertEqual({'test1', 'test2', 'test3', 'test4'}, set(obj_period_names))

    def test_get_obj_period(self):
        self.assertEqual(AsyncExclusivePeriod._get_obj_period(self, 'test1')._name, 'test1')

    def test_get_obj_period_names(self):
        obj_period_names = AsyncExclusivePeriod.get_obj_period_names(self)
        self.assertEqual({'test1', 'test2', 'test3'}, set(obj_period_names))

    async def test_set_get_obj_present_period(self):
        AsyncExclusivePeriod.set_obj_period(self, 'test2')
        self.assertEqual('test2', AsyncExclusivePeriod.get_obj_present_period(self))

    async def test_wait_inside_period(self):
        time1 = asyncio.get_running_loop().time()
        await AsyncExclusivePeriod.wait_inside_period(self, 'test1')
        time2 = asyncio.get_running_loop().time()
        self.assertLessThan(time2 - time1, 0.2)
        asyncio.create_task(self._wait_then_set_period(self, 0.3, 'test3'))
        await AsyncExclusivePeriod.wait_inside_period(self, 'test3')
        time3 = asyncio.get_running_loop().time()
        self.assertGreaterThan(time3 - time2, 0.2)

    async def _wait_then_set_period(self, obj, wait_seconds: float, period_name: str):
        await asyncio.sleep(wait_seconds)
        AsyncExclusivePeriod.set_obj_period(obj, period_name)

    async def test_wait_outside_period(self):
        time1 = asyncio.get_running_loop().time()
        await AsyncExclusivePeriod.wait_outside_period(self, 'test2')
        time2 = asyncio.get_running_loop().time()

        self.assertLessThan(time2 - time1, 0.2)

        asyncio.create_task(self._wait_then_set_period(self, 0.3, 'test3'))
        await AsyncExclusivePeriod.wait_outside_period(self, 'test1')
        time3 = asyncio.get_running_loop().time()
        self.assertGreaterThan(time3 - time2, 0.2)

    async def test_wait_enter_period(self):
        _far_wait_enter_period_helps_test_wait_enter_period_task = asyncio.create_task(
            self._far_wait_enter_period_helps_test_wait_enter_period(self, 'test1'))
        time1 = asyncio.get_running_loop().time()
        asyncio.create_task(self._wait_then_set_period(self, 0.3, 'test3'))
        await AsyncExclusivePeriod.wait_enter_period(self, 'test3')
        time2 = asyncio.get_running_loop().time()
        self.assertGreaterThan(time2 - time1, 0.2)
        asyncio.create_task(self._wait_then_set_period(self, 0.3, 'test1'))
        await _far_wait_enter_period_helps_test_wait_enter_period_task

    async def _far_wait_enter_period_helps_test_wait_enter_period(self, obj, period_name: str):
        time1 = asyncio.get_running_loop().time()
        await AsyncExclusivePeriod.wait_enter_period(obj, period_name)
        time2 = asyncio.get_running_loop().time()
        self.assertGreaterThan(time2 - time1, 0.5)
        self.assertLessThan(time2 - time1, 0.7)

    async def test_wait_exit_period(self):
        _far_wait_exit_period_helps_test_wait_exit_period_task = asyncio.create_task(
            self._far_wait_exit_period_helps_test_wait_exit_period(self, 'test2'))
        time1 = asyncio.get_running_loop().time()
        asyncio.create_task(self._wait_then_set_period(self, 0.3, 'test2'))
        await AsyncExclusivePeriod.wait_exit_period(self, 'test1')
        time2 = asyncio.get_running_loop().time()
        self.assertGreaterThan(time2 - time1, 0.2)
        asyncio.create_task(self._wait_then_set_period(self, 0.3, 'test1'))
        await _far_wait_exit_period_helps_test_wait_exit_period_task

    async def _far_wait_exit_period_helps_test_wait_exit_period(self, obj, period_name: str):
        time1 = asyncio.get_running_loop().time()
        await AsyncExclusivePeriod.wait_exit_period(obj, period_name)
        time2 = asyncio.get_running_loop().time()
        self.assertGreaterThan(time2 - time1, 0.5)
        self.assertLessThan(time2 - time1, 0.7)


if __name__ == '__main__':
    asyncUnittest.run()
