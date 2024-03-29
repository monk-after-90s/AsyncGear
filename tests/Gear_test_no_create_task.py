'''
There is no guarantee of success every time
'''
import asyncio
from AsyncGear import Gear, run_when_enter

import asyncUnittest
from asyncUnittest import AsyncTestCase

from loguru import logger
import sys

logger.remove()
logger.add(sys.stderr, level="INFO")


class TestGearNoCreateTask(AsyncTestCase):
    async def setUp(self) -> None:
        Gear(self).add_periods('test1', 'test2', 'test3')
        self.assertEqual(Gear(self).get_present_period(), 'test1')

    async def test_handle_period_then_set_period(self):
        q = asyncio.Queue()
        # 两个工人
        Gear('worker1').add_periods('waiting', 'working')
        Gear('worker2').add_periods('waiting', 'working')

        async def worker(name: str):
            '''工人等self的test2时期，就工作，工作完再等'''
            while True:
                await(Gear(name).set_period('waiting'))
                await(Gear(self).wait_enter_period('test2'))
                q.put_nowait({"time": asyncio.get_running_loop().time(), 'msg': 'start to work'})
                await(Gear(name).set_period('working'))
                await(asyncio.sleep(1))  # simulate work
                q.put_nowait({"time": asyncio.get_running_loop().time(), 'msg': 'end working'})  # 测试间隔1s
                # 测试在0.5s之后是test1时期

        # 激活两工人
        worker1_task = asyncio.create_task(worker('worker1'))

        worker2_task = asyncio.create_task(worker('worker2'))

        async def wait_worker_accomplish_working_then_set_period_test1():
            '''等待工人干完活就设置self到周期test1'''
            while True:
                wait_worker1_exit_working_task = asyncio.create_task(
                    Gear('worker1').wait_exit_period('working'))
                wait_worker2_exit_working_task = asyncio.create_task(
                    Gear('worker2').wait_exit_period('working'))
                await asyncio.ensure_future(
                    asyncio.gather(wait_worker1_exit_working_task, wait_worker2_exit_working_task))
                await(Gear(self).set_period('test1'))

        wait_worker_accomplish_working_then_set_period_test1_task = \
            asyncio.create_task(wait_worker_accomplish_working_then_set_period_test1())

        async def noticing_in_test2():
            '''提醒工人干活的时期'''
            while True:
                await(Gear(self).wait_inside_period('test2'))
                q.put_nowait(
                    {"time": asyncio.get_running_loop().time(), 'msg': 'In test2, the workers should be working.'})

                await(asyncio.sleep(0.05))  # 测试是处于工作时期内

        noticing_in_test2_task = asyncio.create_task(noticing_in_test2())

        async def set_test2():
            '''只要离开test2时期就1s后设置到test2时期让工人干活'''
            while True:
                await(Gear(self).wait_outside_period('test2'))
                await(asyncio.sleep(1))
                await(Gear(self).set_period('test2'))  # 测试休息1s

        set_test2_task = asyncio.create_task(set_test2())

        work_start_time = None
        work_end_time = None
        work_end_time_count = 0
        tasks = []
        init_time = asyncio.get_running_loop().time()
        while asyncio.get_running_loop().time() - init_time <= 5:
            new_msg = await(q.get())
            if new_msg['msg'] == 'start to work':
                work_start_time = new_msg['time']
                if work_end_time:
                    self.assertEqual(round(work_start_time - work_end_time), 1)

            elif new_msg['msg'] == 'end working':
                work_end_time = new_msg['time']
                self.assertEqual(round(work_end_time - work_start_time), 1)

                async def test_in_test1_period_after_end_working():
                    await(asyncio.sleep(0.5))
                    self.assertEqual('test1', Gear(self).get_present_period())

                tasks.append(asyncio.create_task(test_in_test1_period_after_end_working()))

                # 俩工人第一次完工，复位
                work_end_time_count += 1
                if work_end_time_count % 2 == 0:
                    work_start_time = work_end_time = None
            elif new_msg['msg'] == 'In test2, the workers should be working.':
                if work_start_time:
                    self.assertLessThan(new_msg['time'] - work_start_time, 1)
            q.task_done()
        [await task for task in tasks]

    async def test_add_period(self):
        Gear(self).add_periods('test4')
        self.assertEqual(Gear(self).get_present_period(), 'test1')
        obj_period_names = Gear(self).get_period_names()
        self.assertEqual({'test1', 'test2', 'test3', 'test4'}, set(obj_period_names))

    def test_get_obj_period_names(self):
        obj_period_names = Gear(self).get_period_names()
        self.assertEqual({'test1', 'test2', 'test3'}, set(obj_period_names))

    async def test_set_get_obj_present_period(self):
        await(Gear(self).set_period('test2'))
        self.assertEqual('test2', Gear(self).get_present_period())

        await(Gear(self).set_period('test3'))
        self.assertEqual('test3', Gear(self).get_present_period())
        await(Gear(self).set_period('test1'))

        # idempotent test
        var = True

        @run_when_enter(self, 'test2')
        def enter_test():
            nonlocal var
            var = not var

        # slot_num test
        await(Gear(self).set_period('test2'))
        self.assertEqual(False, var)
        await(Gear(self).set_period('test2'))
        self.assertEqual(False, var)
        await(Gear(self).set_period('test1'))

        ## idempotent test
        await(Gear(self).set_period('test1', slot_num=2))
        self.assertEqual('test1', Gear(self).get_present_period())
        await(Gear(self).set_period('test1', slot_num=2))
        self.assertEqual('test1', Gear(self).get_present_period())
        ## halfway test
        await(Gear(self).set_period('test2', slot_num=3))
        self.assertEqual('test1', Gear(self).get_present_period())
        await(Gear(self).set_period('test2', slot_num=3))
        self.assertEqual('test1', Gear(self).get_present_period())
        await(Gear(self).set_period('test2', slot_num=3))
        self.assertEqual('test2', Gear(self).get_present_period())
        await(Gear(self).set_period('test1'))

        ## interrput test
        self.assertEqual('test1', Gear(self).get_present_period())
        await(Gear(self).set_period('test2', slot_num=3))
        self.assertEqual('test1', Gear(self).get_present_period())
        await(Gear(self).set_period('test2', slot_num=3))
        self.assertEqual('test1', Gear(self).get_present_period())
        await(Gear(self).set_period('test2', slot_num=2))
        self.assertEqual('test1', Gear(self).get_present_period())
        await(Gear(self).set_period('test2', slot_num=2))
        self.assertEqual('test2', Gear(self).get_present_period())
        await(Gear(self).set_period('test1'))
        await(Gear(self).set_period('test2', slot_num=3))
        self.assertEqual('test1', Gear(self).get_present_period())
        await(Gear(self).set_period('test2', slot_num=3))
        self.assertEqual('test1', Gear(self).get_present_period())
        await(Gear(self).set_period('test2', slot_num=3))
        self.assertEqual('test2', Gear(self).get_present_period())
        await(Gear(self).set_period('test1'))

        ## cross set test
        await(Gear(self).set_period('test3', slot_num=3))
        self.assertEqual('test1', Gear(self).get_present_period())
        await(Gear(self).set_period('test2', slot_num=3))
        self.assertEqual('test1', Gear(self).get_present_period())
        await(Gear(self).set_period('test3', slot_num=2))
        self.assertEqual('test1', Gear(self).get_present_period())
        await(Gear(self).set_period('test3', slot_num=2))
        self.assertEqual('test3', Gear(self).get_present_period())
        await(Gear(self).set_period('test2', slot_num=3))
        self.assertEqual('test3', Gear(self).get_present_period())
        await(Gear(self).set_period('test2', slot_num=3))
        self.assertEqual('test2', Gear(self).get_present_period())
        await(Gear(self).set_period('test1'))

    async def test_wait_inside_period(self):
        time1 = asyncio.get_running_loop().time()
        await(Gear(self).wait_inside_period('test1'))
        time2 = asyncio.get_running_loop().time()
        self.assertLessThan(time2 - time1, 0.2)
        asyncio.create_task(self._wait_then_set_period(self, 0.3, 'test3'))
        await(Gear(self).wait_inside_period('test3'))
        time3 = asyncio.get_running_loop().time()
        self.assertGreaterThan(time3 - time2, 0.2)

    async def _wait_then_set_period(self, obj, wait_seconds: float, period_name: str):
        await(asyncio.sleep(wait_seconds))
        await(Gear(obj).set_period(period_name))

    async def test_wait_outside_period(self):
        time1 = asyncio.get_running_loop().time()
        await(Gear(self).wait_outside_period('test2'))
        time2 = asyncio.get_running_loop().time()

        self.assertLessThan(time2 - time1, 0.2)

    async def test_bind_obj_has_dict_property(self):
        class C:
            a = {}

        Gear(C).add_periods('1')
        Gear(C).add_periods('2')
        self.assertEqual('1', Gear(C).get_present_period())
        waiter = asyncio.create_task(Gear(C).wait_enter_period('2'))
        await(Gear(C).set_period('2'))
        await waiter

    async def test_wait_change_period(self):
        waiter_task = asyncio.create_task(Gear(self).wait_change_period())
        asyncio.create_task(Gear(self).set_period('test2'))
        waited = None
        try:
            await asyncio.wait_for(waiter_task, 0.1)
            waited = True
        except asyncio.TimeoutError:
            waited = False
        self.assertIs(waited, True)

        waiter_task = asyncio.create_task(Gear(self).wait_change_period())
        asyncio.get_running_loop().call_later(0.05, Gear(self).sync_set_period, 'test3')
        waited = None
        try:
            await asyncio.wait_for(waiter_task, 0.1)
            waited = True
        except asyncio.TimeoutError:
            waited = False
        self.assertIs(waited, True)

        Gear(self).add_periods('test4')
        waiter_task = asyncio.create_task(Gear(self).wait_change_period())
        asyncio.get_running_loop().call_later(0.05, Gear(self).sync_set_period, 'test4')
        waited = None
        try:
            await asyncio.wait_for(waiter_task, 0.1)
            waited = True
        except asyncio.TimeoutError:
            waited = False
        self.assertIs(waited, True)

        n = 1000

        async def waiter():
            for _ in range(n):
                await Gear(self).wait_change_period()

        waiter_task = asyncio.create_task(waiter())

        for _ in range(n):
            if Gear(self).get_present_period() != 'test2':
                await(Gear(self).set_period('test2'))
            else:
                await(Gear(self).set_period('test1'))

        await asyncio.wait_for(waiter_task, 5)


if __name__ == '__main__':
    asyncUnittest.run()
