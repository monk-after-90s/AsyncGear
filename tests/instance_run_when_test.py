import asyncio

import uvloop

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

import asyncUnittest
from asyncUnittest import AsyncTestCase
from AsyncGear import Gear, when_enter, when_exit, when_inside, when_outside


class TestInstance_run_when(AsyncTestCase):
    async def test_when_ins_enter(self):
        class C:
            def __init__(self):
                Gear(self).add_periods('sleep', 'awaken')
                self.awaken_count = 0
                self.sleep_count = 0

            @when_enter('awaken')
            def f(self):
                self.awaken_count += 1

            @when_enter('awaken')
            async def f1(self):
                self.awaken_count += 1

            @when_enter('sleep')
            def f2(self):
                self.sleep_count += 1

        c = C()
        await asyncio.create_task(Gear(c).set_period('awaken'))
        self.assertEqual(c.awaken_count, 2)
        self.assertEqual(c.sleep_count, 0)
        await asyncio.create_task(Gear(c).set_period('sleep'))
        self.assertEqual(c.awaken_count, 2)
        self.assertEqual(c.sleep_count, 1)
        await asyncio.create_task(Gear(c).set_period('awaken'))
        self.assertEqual(c.awaken_count, 4)
        self.assertEqual(c.sleep_count, 1)

        # queue_blocking test
        ## abandon
        class C:
            def __init__(self):
                Gear(self).add_periods('sleep', 'awaken')
                self.awaken_count = 0

            @when_enter('awaken', 'abandon')
            async def f1(self):
                await asyncio.create_task(asyncio.sleep(0.1))
                self.awaken_count += 1

        c = C()
        await asyncio.create_task(Gear(c).set_period('awaken'))
        await asyncio.create_task(Gear(c).set_period('sleep'))
        await asyncio.create_task(Gear(c).set_period('awaken'))
        await asyncio.create_task(Gear(c).set_period('sleep'))
        self.assertEqual(c.awaken_count, 0)
        await asyncio.create_task(asyncio.sleep(0.15))
        self.assertEqual(c.awaken_count, 1)
        await asyncio.create_task(asyncio.sleep(0.25))
        self.assertEqual(c.awaken_count, 1)

        ## non_block
        class C:
            def __init__(self):
                Gear(self).add_periods('sleep', 'awaken')
                self.awaken_count = 0

            @when_enter('awaken', 'non_block')
            async def f1(self):
                await asyncio.create_task(asyncio.sleep(0.1))
                self.awaken_count += 1

        c = C()
        await asyncio.create_task(Gear(c).set_period('awaken'))
        await asyncio.create_task(Gear(c).set_period('sleep'))
        await asyncio.create_task(Gear(c).set_period('awaken'))
        await asyncio.create_task(Gear(c).set_period('sleep'))
        self.assertEqual(c.awaken_count, 0)
        await asyncio.create_task(asyncio.sleep(0.15))
        self.assertEqual(c.awaken_count, 2)

        ## queue
        class C:
            def __init__(self):
                Gear(self).add_periods('sleep', 'awaken')
                self.awaken_count = 0

            @when_enter('awaken', 'queue')
            async def f1(self):
                await asyncio.create_task(asyncio.sleep(0.1))
                self.awaken_count += 1

        c = C()
        await asyncio.create_task(Gear(c).set_period('awaken'))
        await asyncio.create_task(Gear(c).set_period('sleep'))
        await asyncio.create_task(Gear(c).set_period('awaken'))
        await asyncio.create_task(Gear(c).set_period('sleep'))
        self.assertEqual(c.awaken_count, 0)
        await asyncio.create_task(asyncio.sleep(0.15))
        self.assertEqual(c.awaken_count, 1)
        await asyncio.create_task(asyncio.sleep(0.25))
        self.assertEqual(c.awaken_count, 2)

    async def test_when_ins_exit(self):
        class C:
            def __init__(self):
                Gear(self).add_periods('sleep', 'awaken')
                self.awaken_exit_count = 0
                self.sleep_exit_count = 0

            @when_exit('awaken')
            def f(self):
                self.awaken_exit_count += 1

            @when_exit('awaken')
            async def f1(self):
                self.awaken_exit_count += 1

            @when_exit('sleep')
            def f2(self):
                self.sleep_exit_count += 1

        c = C()
        await asyncio.create_task(Gear(c).set_period('awaken'))
        self.assertEqual(c.sleep_exit_count, 1)
        self.assertEqual(c.awaken_exit_count, 0)
        await asyncio.create_task(Gear(c).set_period('sleep'))
        self.assertEqual(c.sleep_exit_count, 1)
        self.assertEqual(c.awaken_exit_count, 2)
        await asyncio.create_task(Gear(c).set_period('awaken'))
        self.assertEqual(c.sleep_exit_count, 2)
        self.assertEqual(c.awaken_exit_count, 2)

        # queue_blocking test
        ## abandon
        class C:
            def __init__(self):
                Gear(self).add_periods('sleep', 'awaken')
                self.awaken_count = 0

            @when_exit('sleep', 'abandon')
            async def f1(self):
                await asyncio.create_task(asyncio.sleep(0.1))
                self.awaken_count += 1

        c = C()
        await asyncio.create_task(Gear(c).set_period('awaken'))
        await asyncio.create_task(Gear(c).set_period('sleep'))
        await asyncio.create_task(Gear(c).set_period('awaken'))
        await asyncio.create_task(Gear(c).set_period('sleep'))
        self.assertEqual(c.awaken_count, 0)
        await asyncio.create_task(asyncio.sleep(0.15))
        self.assertEqual(c.awaken_count, 1)
        await asyncio.create_task(asyncio.sleep(0.25))
        self.assertEqual(c.awaken_count, 1)

        ## non_block
        class C:
            def __init__(self):
                Gear(self).add_periods('sleep', 'awaken')
                self.awaken_count = 0

            @when_exit('sleep', 'non_block')
            async def f1(self):
                await asyncio.create_task(asyncio.sleep(0.1))
                self.awaken_count += 1

        c = C()
        await asyncio.create_task(Gear(c).set_period('awaken'))
        await asyncio.create_task(Gear(c).set_period('sleep'))
        await asyncio.create_task(Gear(c).set_period('awaken'))
        await asyncio.create_task(Gear(c).set_period('sleep'))
        self.assertEqual(c.awaken_count, 0)
        await asyncio.create_task(asyncio.sleep(0.15))
        self.assertEqual(c.awaken_count, 2)

        ## queue
        class C:
            def __init__(self):
                Gear(self).add_periods('sleep', 'awaken')
                self.awaken_count = 0

            @when_exit('sleep', 'queue')
            async def f1(self):
                await asyncio.create_task(asyncio.sleep(0.1))
                self.awaken_count += 1

        c = C()
        await asyncio.create_task(Gear(c).set_period('awaken'))
        await asyncio.create_task(Gear(c).set_period('sleep'))
        await asyncio.create_task(Gear(c).set_period('awaken'))
        await asyncio.create_task(Gear(c).set_period('sleep'))
        self.assertEqual(c.awaken_count, 0)
        await asyncio.create_task(asyncio.sleep(0.15))
        self.assertEqual(c.awaken_count, 1)
        await asyncio.create_task(asyncio.sleep(0.25))
        self.assertEqual(c.awaken_count, 2)

    async def test_when_ins_inside(self):
        class C:
            def __init__(self):
                Gear(self).add_periods('sleep', 'awaken')
                self.awaken_count = 0

            @when_inside('awaken')
            async def f1(self):
                await asyncio.create_task(asyncio.sleep(0.1))
                self.awaken_count += 1

        c = C()
        await asyncio.create_task(Gear(c).set_period('awaken'))
        await asyncio.create_task(asyncio.sleep(0.25))
        await asyncio.create_task(Gear(c).set_period('sleep'))
        self.assertEqual(c.awaken_count, 2)

    async def test_when_ins_outside(self):
        class C:
            def __init__(self):
                Gear(self).add_periods('sleep', 'awaken')
                self.awaken_count = 0

            @when_outside('sleep')
            async def f1(self):
                await asyncio.create_task(asyncio.sleep(0.1))
                self.awaken_count += 1

        c = C()
        await asyncio.create_task(Gear(c).set_period('awaken'))
        await asyncio.create_task(asyncio.sleep(0.299))
        await asyncio.create_task(Gear(c).set_period('sleep'))
        self.assertEqual(c.awaken_count, 2)

    async def test_class_method_when_enter(self):
        class C:
            awaken_count = 0
            sleep_count = 0

            @when_enter('awaken')
            @classmethod
            def f(cls):
                cls.awaken_count += 1

            @when_enter('awaken')
            @classmethod
            async def f1(cls):
                cls.awaken_count += 1

            @when_enter('sleep')
            @classmethod
            def f2(cls):
                cls.sleep_count += 1

        Gear(C).add_periods('sleep', 'awaken')
        await asyncio.create_task(Gear(C).set_period('awaken'))
        self.assertEqual(C.awaken_count, 2)
        self.assertEqual(C.sleep_count, 0)
        await asyncio.create_task(Gear(C).set_period('sleep'))
        self.assertEqual(C.awaken_count, 2)
        self.assertEqual(C.sleep_count, 1)
        await asyncio.create_task(Gear(C).set_period('awaken'))
        self.assertEqual(C.awaken_count, 4)
        self.assertEqual(C.sleep_count, 1)

        # queue_blocking test
        ## abandon
        class C:
            awaken_count = 0

            @when_enter('awaken', 'abandon')
            @classmethod
            async def f1(cls):
                await asyncio.create_task(asyncio.sleep(0.1))
                cls.awaken_count += 1

        Gear(C).add_periods('sleep', 'awaken')
        await asyncio.create_task(Gear(C).set_period('awaken'))
        await asyncio.create_task(Gear(C).set_period('sleep'))
        await asyncio.create_task(Gear(C).set_period('awaken'))
        await asyncio.create_task(Gear(C).set_period('sleep'))
        self.assertEqual(C.awaken_count, 0)
        await asyncio.create_task(asyncio.sleep(0.15))
        self.assertEqual(C.awaken_count, 1)
        await asyncio.create_task(asyncio.sleep(0.25))
        self.assertEqual(C.awaken_count, 1)

        ## non_block
        class C:
            awaken_count = 0

            @when_enter('awaken', 'non_block')
            @classmethod
            async def f1(cls):
                await asyncio.create_task(asyncio.sleep(0.1))
                cls.awaken_count += 1

        Gear(C).add_periods('sleep', 'awaken')
        await asyncio.create_task(Gear(C).set_period('awaken'))
        await asyncio.create_task(Gear(C).set_period('sleep'))
        await asyncio.create_task(Gear(C).set_period('awaken'))
        await asyncio.create_task(Gear(C).set_period('sleep'))
        self.assertEqual(C.awaken_count, 0)
        await asyncio.create_task(asyncio.sleep(0.15))
        self.assertEqual(C.awaken_count, 2)

        ## queue
        class C:
            awaken_count = 0

            @when_enter('awaken', 'queue')
            @classmethod
            async def f1(cls):
                await asyncio.create_task(asyncio.sleep(0.1))
                cls.awaken_count += 1

        Gear(C).add_periods('sleep', 'awaken')
        await asyncio.create_task(Gear(C).set_period('awaken'))
        await asyncio.create_task(Gear(C).set_period('sleep'))
        await asyncio.create_task(Gear(C).set_period('awaken'))
        await asyncio.create_task(Gear(C).set_period('sleep'))
        self.assertEqual(C.awaken_count, 0)
        await asyncio.create_task(asyncio.sleep(0.15))
        self.assertEqual(C.awaken_count, 1)
        await asyncio.create_task(asyncio.sleep(0.25))
        self.assertEqual(C.awaken_count, 2)

    async def test_class_method_when_exit(self):
        class C:
            awaken_count = 0
            sleep_count = 0

            @when_exit('sleep')
            @classmethod
            def f(cls):
                cls.awaken_count += 1

            @when_exit('sleep')
            @classmethod
            async def f1(cls):
                cls.awaken_count += 1

            @when_exit('awaken')
            @classmethod
            def f2(cls):
                cls.sleep_count += 1

        Gear(C).add_periods('sleep', 'awaken')
        await asyncio.create_task(Gear(C).set_period('awaken'))
        self.assertEqual(C.awaken_count, 2)
        self.assertEqual(C.sleep_count, 0)
        await asyncio.create_task(Gear(C).set_period('sleep'))
        self.assertEqual(C.awaken_count, 2)
        self.assertEqual(C.sleep_count, 1)
        await asyncio.create_task(Gear(C).set_period('awaken'))
        self.assertEqual(C.awaken_count, 4)
        self.assertEqual(C.sleep_count, 1)

        # queue_blocking test
        ## abandon
        class C:
            awaken_count = 0

            @when_exit('sleep', 'abandon')
            @classmethod
            async def f1(cls):
                await asyncio.create_task(asyncio.sleep(0.1))
                cls.awaken_count += 1

        Gear(C).add_periods('sleep', 'awaken')
        await asyncio.create_task(Gear(C).set_period('awaken'))
        await asyncio.create_task(Gear(C).set_period('sleep'))
        await asyncio.create_task(Gear(C).set_period('awaken'))
        await asyncio.create_task(Gear(C).set_period('sleep'))
        self.assertEqual(C.awaken_count, 0)
        await asyncio.create_task(asyncio.sleep(0.15))
        self.assertEqual(C.awaken_count, 1)
        await asyncio.create_task(asyncio.sleep(0.25))
        self.assertEqual(C.awaken_count, 1)

        ## non_block
        class C:
            awaken_count = 0

            @when_exit('sleep', 'non_block')
            @classmethod
            async def f1(cls):
                await asyncio.create_task(asyncio.sleep(0.1))
                cls.awaken_count += 1

        Gear(C).add_periods('sleep', 'awaken')
        await asyncio.create_task(Gear(C).set_period('awaken'))
        await asyncio.create_task(Gear(C).set_period('sleep'))
        await asyncio.create_task(Gear(C).set_period('awaken'))
        await asyncio.create_task(Gear(C).set_period('sleep'))
        self.assertEqual(C.awaken_count, 0)
        await asyncio.create_task(asyncio.sleep(0.15))
        self.assertEqual(C.awaken_count, 2)

        ## queue
        class C:
            awaken_count = 0

            @when_exit('sleep', 'queue')
            @classmethod
            async def f1(cls):
                await asyncio.create_task(asyncio.sleep(0.1))
                cls.awaken_count += 1

        Gear(C).add_periods('sleep', 'awaken')
        await asyncio.create_task(Gear(C).set_period('awaken'))
        await asyncio.create_task(Gear(C).set_period('sleep'))
        await asyncio.create_task(Gear(C).set_period('awaken'))
        await asyncio.create_task(Gear(C).set_period('sleep'))
        self.assertEqual(C.awaken_count, 0)
        await asyncio.create_task(asyncio.sleep(0.15))
        self.assertEqual(C.awaken_count, 1)
        await asyncio.create_task(asyncio.sleep(0.25))
        self.assertEqual(C.awaken_count, 2)

    async def test_class_method_when_inside(self):
        class C:
            awaken_count = 0

            @when_inside('awaken')
            @classmethod
            async def f1(cls):
                await asyncio.create_task(asyncio.sleep(0.1))
                cls.awaken_count += 1

        Gear(C).add_periods('sleep', 'awaken')
        await asyncio.create_task(Gear(C).set_period('awaken'))
        await asyncio.create_task(asyncio.sleep(0.25))
        await asyncio.create_task(Gear(C).set_period('sleep'))
        self.assertEqual(C.awaken_count, 2)

    async def test_class_method_when_outside(self):
        class C:
            awaken_count = 0

            @when_outside('sleep')
            @classmethod
            async def f1(cls):
                await asyncio.create_task(asyncio.sleep(0.1))
                cls.awaken_count += 1

        Gear(C).add_periods('sleep', 'awaken')
        await asyncio.create_task(Gear(C).set_period('awaken'))
        await asyncio.create_task(asyncio.sleep(0.25))
        await asyncio.create_task(Gear(C).set_period('sleep'))
        self.assertEqual(C.awaken_count, 2)


if __name__ == '__main__':
    asyncUnittest.run()
