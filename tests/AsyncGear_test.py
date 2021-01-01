import asyncio

from asyncUnittest import AsyncTestCase
import asyncUnittest

from AsyncGear.AsyncGear import AsyncGear
import uvloop

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class TestAsyncGear(AsyncTestCase):
    async def setUp(self) -> None:
        AsyncGear.create_obj_periods(self, 'test1', 'test2', 'test3')
        self.assertEqual(AsyncGear.get_obj_present_period(self), 'test1')

    async def test_handle_period_then_set_period(self):
        q = asyncio.Queue()
        # 两个工人
        AsyncGear.create_obj_periods('worker1', 'waiting', 'working')

        AsyncGear.create_obj_periods('worker2', 'waiting', 'working')

        async def worker(name: str):
            '''工人等self的test2时期，就工作，工作完再等'''
            while True:
                await asyncio.create_task(AsyncGear.set_obj_period(name, 'waiting'))
                await asyncio.create_task(AsyncGear.wait_enter_period(self, 'test2'))
                q.put_nowait({"time": asyncio.get_running_loop().time(), 'msg': 'start to work'})
                await asyncio.create_task(AsyncGear.set_obj_period(name, 'working'))
                await asyncio.create_task(asyncio.sleep(1))  # simulate work
                q.put_nowait({"time": asyncio.get_running_loop().time(), 'msg': 'end working'})  # 测试间隔1s
                # 测试在0.5s之后是test1时期

        # 激活两工人
        worker1_task = asyncio.create_task(worker('worker1'))

        worker2_task = asyncio.create_task(worker('worker2'))

        async def wait_worker_accomplish_working_then_set_period_test1():
            '''等待工人干完活就设置self到周期test1'''
            while True:
                wait_worker1_exit_working_task = asyncio.create_task(
                    AsyncGear.wait_exit_period('worker1', 'working'))
                wait_worker2_exit_working_task = asyncio.create_task(
                    AsyncGear.wait_exit_period('worker2', 'working'))
                await asyncio.ensure_future(
                    asyncio.gather(wait_worker1_exit_working_task, wait_worker2_exit_working_task))
                await asyncio.create_task(AsyncGear.set_obj_period(self, 'test1'))

        wait_worker_accomplish_working_then_set_period_test1_task = \
            asyncio.create_task(wait_worker_accomplish_working_then_set_period_test1())

        async def noticing_in_test2():
            '''提醒工人干活的时期'''
            while True:
                await asyncio.create_task(AsyncGear.wait_inside_period(self, 'test2'))
                q.put_nowait(
                    {"time": asyncio.get_running_loop().time(), 'msg': 'In test2, the workers should be working.'})

                await asyncio.create_task(asyncio.sleep(0.05))  # 测试是处于工作时期内

        noticing_in_test2_task = asyncio.create_task(noticing_in_test2())

        async def set_test2():
            '''只要离开test2时期就1s后设置到test2时期让工人干活'''
            while True:
                await asyncio.create_task(AsyncGear.wait_outside_period(self, 'test2'))
                await asyncio.create_task(asyncio.sleep(1))
                await asyncio.create_task(AsyncGear.set_obj_period(self, 'test2'))  # 测试休息1s

        set_test2_task = asyncio.create_task(set_test2())

        work_start_time = None
        work_end_time = None
        work_end_time_count = 0
        tasks = []
        init_time = asyncio.get_running_loop().time()
        while asyncio.get_running_loop().time() - init_time <= 5:
            new_msg = await asyncio.create_task(q.get())
            if new_msg['msg'] == 'start to work':
                work_start_time = new_msg['time']
                if work_end_time:
                    self.assertEqual(round(work_start_time - work_end_time), 1)

            elif new_msg['msg'] == 'end working':
                work_end_time = new_msg['time']
                self.assertEqual(round(work_end_time - work_start_time), 1)

                async def test_in_test1_period_after_end_working():
                    await asyncio.create_task(asyncio.sleep(0.5))
                    self.assertEqual('test1', AsyncGear.get_obj_present_period(self))

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
        AsyncGear.add_period(self, 'test4')
        self.assertEqual(AsyncGear.get_obj_present_period(self), 'test1')
        obj_period_names = AsyncGear.get_obj_period_names(self)
        self.assertEqual({'test1', 'test2', 'test3', 'test4'}, set(obj_period_names))

    def test_get_obj_period(self):
        self.assertEqual(AsyncGear._get_obj_period(self, 'test1')._name, 'test1')

    def test_get_obj_period_names(self):
        obj_period_names = AsyncGear.get_obj_period_names(self)
        self.assertEqual({'test1', 'test2', 'test3'}, set(obj_period_names))

    async def test_set_get_obj_present_period(self):
        await asyncio.create_task(AsyncGear.set_obj_period(self, 'test2'))
        self.assertEqual('test2', AsyncGear.get_obj_present_period(self))

        await asyncio.create_task(AsyncGear.set_obj_period(self, 'test3'))
        self.assertEqual('test3', AsyncGear.get_obj_present_period(self))

    async def test_wait_inside_period(self):
        time1 = asyncio.get_running_loop().time()
        await asyncio.create_task(AsyncGear.wait_inside_period(self, 'test1'))
        time2 = asyncio.get_running_loop().time()
        self.assertLessThan(time2 - time1, 0.2)
        asyncio.create_task(self._wait_then_set_period(self, 0.3, 'test3'))
        await asyncio.create_task(AsyncGear.wait_inside_period(self, 'test3'))
        time3 = asyncio.get_running_loop().time()
        self.assertGreaterThan(time3 - time2, 0.2)

    async def _wait_then_set_period(self, obj, wait_seconds: float, period_name: str):
        await asyncio.create_task(asyncio.sleep(wait_seconds))
        await asyncio.create_task(AsyncGear.set_obj_period(obj, period_name))

    async def test_wait_outside_period(self):
        time1 = asyncio.get_running_loop().time()
        await asyncio.create_task(AsyncGear.wait_outside_period(self, 'test2'))
        time2 = asyncio.get_running_loop().time()

        self.assertLessThan(time2 - time1, 0.2)

        asyncio.create_task(self._wait_then_set_period(self, 0.3, 'test3'))
        await asyncio.create_task(AsyncGear.wait_outside_period(self, 'test1'))
        time3 = asyncio.get_running_loop().time()
        self.assertGreaterThan(time3 - time2, 0.2)

    async def test_wait_enter_period(self):
        _far_wait_enter_period_helps_test_wait_enter_period_task = asyncio.create_task(
            self._far_wait_enter_period_helps_test_wait_enter_period(self, 'test1'))
        time1 = asyncio.get_running_loop().time()
        asyncio.create_task(self._wait_then_set_period(self, 0.3, 'test3'))
        await asyncio.create_task(AsyncGear.wait_enter_period(self, 'test3'))
        time2 = asyncio.get_running_loop().time()
        self.assertGreaterThan(time2 - time1, 0.2)
        asyncio.create_task(self._wait_then_set_period(self, 0.3, 'test1'))
        await _far_wait_enter_period_helps_test_wait_enter_period_task

    async def _far_wait_enter_period_helps_test_wait_enter_period(self, obj, period_name: str):
        time1 = asyncio.get_running_loop().time()
        await asyncio.create_task(AsyncGear.wait_enter_period(obj, period_name))
        time2 = asyncio.get_running_loop().time()
        self.assertGreaterThan(time2 - time1, 0.5)
        self.assertLessThan(time2 - time1, 0.7)

    async def test_wait_exit_period(self):
        _far_wait_exit_period_helps_test_wait_exit_period_task = asyncio.create_task(
            self._far_wait_exit_period_helps_test_wait_exit_period(self, 'test2'))
        time1 = asyncio.get_running_loop().time()
        asyncio.create_task(self._wait_then_set_period(self, 0.3, 'test2'))
        await asyncio.create_task(AsyncGear.wait_exit_period(self, 'test1'))
        time2 = asyncio.get_running_loop().time()
        self.assertGreaterThan(time2 - time1, 0.2)
        asyncio.create_task(self._wait_then_set_period(self, 0.3, 'test1'))
        await _far_wait_exit_period_helps_test_wait_exit_period_task

    async def _far_wait_exit_period_helps_test_wait_exit_period(self, obj, period_name: str):
        time1 = asyncio.get_running_loop().time()
        await asyncio.create_task(AsyncGear.wait_exit_period(obj, period_name))
        time2 = asyncio.get_running_loop().time()
        self.assertGreaterThan(time2 - time1, 0.5)
        self.assertLessThan(time2 - time1, 0.7)


if __name__ == '__main__':
    asyncUnittest.run()
