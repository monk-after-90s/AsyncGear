'''
Transfer an object to its gear, as an interface.
'''
import asyncio

from .AsyncGear import AsyncGear


class Gear:
    # last_set_period = {}

    def __init__(self, obj):
        self.obj = obj

    def add_periods(self, *new_period_names: str):
        '''
        Dynamically add periods for some object.

        :return:
        '''
        for new_period_name in new_period_names:
            AsyncGear.add_period(self.obj, new_period_name)

    def get_present_period(self):
        return AsyncGear.get_obj_present_period(self.obj)

    def get_period_names(self):
        return AsyncGear.get_obj_period_names(self.obj)

    async def set_period(self, period_name: str, slot_num: int = 1):
        '''
        Set obj to period period_name.

        :param period_name:
        :param slot_num: Attention! Do not use it if you do not understand it!
                slot_num means that only after slot_num times Gear(obj).set_period(period_name,slot_num) run
                (present time included), the period of Gear(obj) could really be set to period_name, which is interrupted
                if among these times set_period run a different slot_num is given. Then the procedure is refreshed.
        :return:
        '''

        if self.get_present_period() != period_name:
            await asyncio.create_task(self.wait_outside_period(period_name))
        else:
            await asyncio.create_task(self.wait_inside_period(period_name))
        try:
            return await asyncio.create_task(AsyncGear.set_obj_period(self.obj, period_name, slot_num))
        finally:
            # self.last_set_period[self.obj] = period_name
            if self.get_present_period() != period_name:
                await asyncio.create_task(self.wait_outside_period(period_name))
            else:
                await asyncio.create_task(self.wait_inside_period(period_name))

    async def wait_inside_period(self, period_name: str):
        return await asyncio.create_task(AsyncGear.wait_inside_period(self.obj, period_name))

    async def wait_outside_period(self, period_name: str):
        return await asyncio.create_task(AsyncGear.wait_outside_period(self.obj, period_name))

    async def wait_enter_period(self, period_name: str):
        return await asyncio.create_task(AsyncGear.wait_enter_period(self.obj, period_name))

    async def wait_exit_period(self, period_name: str):
        return await asyncio.create_task(AsyncGear.wait_exit_period(self.obj, period_name))

    # def when_enter(self, period_name: str, queue_blocking='abandon'):
    #     return run_when_enter(self.obj, period_name, queue_blocking)
    #
    # def when_exit(self, period_name: str, queue_blocking='abandon'):
    #     return run_when_exit(self.obj, period_name, queue_blocking)
    #
    # def when_inside(self, period_name: str, queue_blocking='abandon'):
    #     return run_when_inside(self.obj, period_name, queue_blocking)
    #
    # def when_outside(self, period_name: str, queue_blocking='abandon'):
    #     return run_when_outside(self.obj, period_name, queue_blocking)
