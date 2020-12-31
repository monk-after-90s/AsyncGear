import asyncio

import uvloop

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
from asyncUnittest import AsyncTestCase
import asyncUnittest  # todo 升级
from AsyncGear import run_when_inside, run_when_exit, run_when_enter, run_when_outside, AsyncGear


class TestRunWhen(AsyncTestCase):
    async def setUp(self) -> None:
        AsyncGear.create_obj_periods(self, 'sleep', 'awaken')
        self.assertEqual('sleep', AsyncGear.get_obj_present_period(self))

    async def test_multi_callback(self):
        var1 = False

        @run_when_enter(self, 'awaken', 'abandon')
        async def enter_test():
            await asyncio.create_task(asyncio.sleep(0.1))
            nonlocal var1
            if var1:
                var1 = False
            else:
                var1 = True

        @run_when_enter(self, 'awaken', 'abandon')
        async def enter_test2():
            await asyncio.create_task(asyncio.sleep(0.1))
            nonlocal var1
            if var1:
                var1 = False
            else:
                var1 = True

        await asyncio.create_task(AsyncGear.set_obj_period(self, 'awaken'))
        self.assertIs(var1, False)

    async def test_run_when_enter(self):
        # normal function, simple test
        var = False

        @run_when_enter(self, 'awaken')
        def enter_test():
            nonlocal var
            var = True

        enter_test()
        self.assertIs(var, True)

        var = False

        await asyncio.create_task(AsyncGear.set_obj_period(self, 'awaken'))
        self.assertEqual('awaken', AsyncGear.get_obj_present_period(self))
        self.assertIs(var, True)
        var = False
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'sleep'))

        # test 3 situations for coroutine functions

        var1 = False

        @run_when_enter(self, 'awaken', 'abandon')
        async def enter_test():
            await asyncio.create_task(asyncio.sleep(0.1))
            nonlocal var1
            if var1:
                var1 = False
            else:
                var1 = True

        await asyncio.create_task(enter_test())
        self.assertIs(var1, True)
        var1 = False

        ## abandon
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'awaken'))
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'sleep'))
        await asyncio.create_task(asyncio.sleep(0.15))
        self.assertIs(var1, True)
        var1 = False

        await asyncio.create_task(AsyncGear.set_obj_period(self, 'awaken'))
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'sleep'))
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'awaken'))
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'sleep'))
        await asyncio.create_task(asyncio.sleep(0.15))
        self.assertIs(var1, True)
        var1 = False

        ## non_block
        var2 = False

        @run_when_enter(self, 'awaken', 'non_block')
        async def enter_test():
            await asyncio.create_task(asyncio.sleep(0.1))
            nonlocal var2
            if var2:
                var2 = False
            else:
                var2 = True

        await asyncio.create_task(AsyncGear.set_obj_period(self, 'awaken'))
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'sleep'))
        await asyncio.create_task(asyncio.sleep(0.15))
        self.assertIs(var2, True)
        var2 = False

        await asyncio.create_task(AsyncGear.set_obj_period(self, 'awaken'))
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'sleep'))
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'awaken'))
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'sleep'))
        await asyncio.create_task(asyncio.sleep(0.15))
        self.assertIs(var2, False)
        var2 = False

        await asyncio.create_task(AsyncGear.set_obj_period(self, 'awaken'))
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'sleep'))
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'awaken'))
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'sleep'))
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'awaken'))
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'sleep'))
        await asyncio.create_task(asyncio.sleep(0.15))
        self.assertIs(var2, True)
        var2 = False
        ## queue
        var3 = False

        fs = []

        @run_when_enter(self, 'awaken', 'queue')
        async def enter_test():
            f = asyncio.get_running_loop().create_future()
            fs.append(f)
            await asyncio.create_task(asyncio.sleep(0.1))
            nonlocal var3
            if var3:
                var3 = False
            else:
                var3 = True
            f.set_result(None)
            fs.remove(f)

        time = asyncio.get_running_loop().time()
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'awaken'))
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'sleep'))
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'awaken'))
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'sleep'))
        await asyncio.create_task(asyncio.sleep(0.15))
        [await asyncio.ensure_future(f) for f in fs]
        self.assertEqual(0.1 * 2, round(asyncio.get_running_loop().time() - time, 1))
        self.assertEqual(var3, False)
        time = asyncio.get_running_loop().time()
        var3 = False

        await asyncio.create_task(AsyncGear.set_obj_period(self, 'awaken'))
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'sleep'))
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'awaken'))
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'sleep'))
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'awaken'))
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'sleep'))
        await asyncio.create_task(asyncio.sleep(0.25))
        [await asyncio.ensure_future(f) for f in fs]
        self.assertEqual(round(0.1 * 3, 1), round(asyncio.get_running_loop().time() - time, 1))
        self.assertEqual(var3, True)
        time = asyncio.get_running_loop().time()
        var3 = False

    async def test_run_when_exit(self):
        # normal function, simple test
        var = False

        @run_when_exit(self, 'sleep')
        def exit_test():
            nonlocal var
            var = True

        exit_test()
        self.assertIs(var, True)

        var = False

        await asyncio.create_task(AsyncGear.set_obj_period(self, 'awaken'))
        self.assertEqual('awaken', AsyncGear.get_obj_present_period(self))
        self.assertIs(var, True)
        var = False
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'sleep'))

        # test 3 situations for coroutine functions

        var1 = False

        @run_when_exit(self, 'sleep', 'abandon')
        async def exit_test():
            await asyncio.create_task(asyncio.sleep(0.1))
            nonlocal var1
            if var1:
                var1 = False
            else:
                var1 = True

        await asyncio.create_task(exit_test())
        self.assertIs(var1, True)
        var1 = False

        ## abandon
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'awaken'))
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'sleep'))
        await asyncio.create_task(asyncio.sleep(0.15))
        self.assertIs(var1, True)
        var1 = False

        await asyncio.create_task(AsyncGear.set_obj_period(self, 'awaken'))
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'sleep'))
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'awaken'))
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'sleep'))
        await asyncio.create_task(asyncio.sleep(0.15))
        self.assertIs(var1, True)
        var1 = False

        ## non_block
        var2 = False

        @run_when_exit(self, 'sleep', 'non_block')
        async def exit_test():
            await asyncio.create_task(asyncio.sleep(0.1))
            nonlocal var2
            if var2:
                var2 = False
            else:
                var2 = True

        await asyncio.create_task(AsyncGear.set_obj_period(self, 'awaken'))
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'sleep'))
        await asyncio.create_task(asyncio.sleep(0.15))
        self.assertIs(var2, True)
        var2 = False

        await asyncio.create_task(AsyncGear.set_obj_period(self, 'awaken'))
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'sleep'))
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'awaken'))
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'sleep'))
        await asyncio.create_task(asyncio.sleep(0.15))
        self.assertIs(var2, False)
        var2 = False

        await asyncio.create_task(AsyncGear.set_obj_period(self, 'awaken'))
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'sleep'))
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'awaken'))
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'sleep'))
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'awaken'))
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'sleep'))
        await asyncio.create_task(asyncio.sleep(0.15))
        self.assertIs(var2, True)
        var2 = False
        ## queue
        var3 = False

        fs = []

        @run_when_exit(self, 'sleep', 'queue')
        async def exit_test():
            f = asyncio.get_running_loop().create_future()
            fs.append(f)
            await asyncio.create_task(asyncio.sleep(0.1))
            nonlocal var3
            if var3:
                var3 = False
            else:
                var3 = True
            f.set_result(None)
            fs.remove(f)

        time = asyncio.get_running_loop().time()
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'awaken'))
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'sleep'))
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'awaken'))
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'sleep'))
        await asyncio.create_task(asyncio.sleep(0.15))
        [await f for f in fs]
        self.assertEqual(0.1 * 2, round(asyncio.get_running_loop().time() - time, 1))
        self.assertEqual(var3, False)
        time = asyncio.get_running_loop().time()
        var3 = False

        await asyncio.create_task(AsyncGear.set_obj_period(self, 'awaken'))
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'sleep'))
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'awaken'))
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'sleep'))
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'awaken'))
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'sleep'))
        await asyncio.create_task(asyncio.sleep(0.25))
        [await f for f in fs]
        self.assertEqual(round(0.1 * 3, 1), round(asyncio.get_running_loop().time() - time, 1))
        self.assertEqual(var3, True)
        time = asyncio.get_running_loop().time()
        var3 = False

    async def test_run_when_inside(self):
        # normal function, simple test
        var = False

        @run_when_inside(self, 'awaken')
        def inside_test():
            nonlocal var
            var = True

        inside_test()
        self.assertIs(var, True)

        var = False

        # test 3 situations for coroutine functions

        ## abandon
        var1 = 0

        @run_when_inside(self, 'awaken', 'abandon')
        async def inside_test():
            await asyncio.create_task(asyncio.sleep(0.1))
            nonlocal var1
            var1 += 1

        await asyncio.create_task(AsyncGear.set_obj_period(self, 'awaken'))
        await asyncio.create_task(asyncio.sleep(0.35))
        self.assertEqual(var1, 3)
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'sleep'))
        ## non_block
        var2 = 0

        @run_when_inside(self, 'awaken', 'non_block')
        async def inside_test():
            await asyncio.create_task(asyncio.sleep(0.1))
            nonlocal var2
            var2 += 1

        await asyncio.create_task(AsyncGear.set_obj_period(self, 'awaken'))
        await asyncio.create_task(asyncio.sleep(1))
        self.assertGreaterThan(var2, 100)
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'sleep'))
        ## queue
        var3 = 0

        @run_when_inside(self, 'awaken', 'queue')
        async def inside_test():
            await asyncio.create_task(asyncio.sleep(0.1))
            nonlocal var3
            var3 += 1

        await asyncio.create_task(AsyncGear.set_obj_period(self, 'awaken'))
        await asyncio.create_task(asyncio.sleep(0.35))
        self.assertEqual(var3, 3)
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'sleep'))


if __name__ == '__main__':
    asyncUnittest.run()

    # async def main():
    #     AsyncGear.create_obj_periods('obj', 'sleep', 'awaken')
    #     assert 'sleep' == AsyncGear.get_obj_present_period('obj')
    #
    #     async def delay_set_period(seconds, period_name):
    #         await asyncio.sleep(seconds)
    #         AsyncGear.set_obj_period('obj', period_name)
    #
    #     asyncio.create_task(delay_set_period(1, 'awaken'))
    #     await AsyncGear.wait_enter_period('obj', 'awaken')
    #     assert 'awaken' == AsyncGear.get_obj_present_period('obj')
    #     print('Over')
    #
    #     loop.stop()
    #
    #
    # async def main2():
    #     AsyncGear.create_obj_periods('obj', 'sleep', 'awaken')
    #     assert 'sleep' == AsyncGear.get_obj_present_period('obj')
    #
    #     async def wait_period(period_name):
    #         await AsyncGear.wait_enter_period('obj', period_name)
    #         print('Over')
    #         loop.stop()
    #
    #     asyncio.create_task(wait_period('awaken'))
    #
    #     await asyncio.sleep(0)
    #     AsyncGear.set_obj_period('obj', 'awaken')
    #     assert 'awaken' == AsyncGear.get_obj_present_period('obj')
    #
    #
    # loop = asyncio.get_event_loop()
    # loop.create_task(main2())
    # loop.run_forever()
