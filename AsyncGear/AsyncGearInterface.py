'''
Transfer an object to its gear, as an interface.
'''
import asyncio

from .AsyncGear import AsyncGear


# from abc import ABCMeta, abstractmethod

#
# class AsyncGearInterface(metaclass=ABCMeta):
#     '''
#         Used in a coroutine.
#     '''
#     @abstractmethod
#     def add_
class Gear:

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

    async def set_period(self, period_name: str):
        return await asyncio.create_task(AsyncGear.set_obj_period(self.obj, period_name))

    async def wait_inside_period(self, period_name: str):
        return await asyncio.create_task(AsyncGear.wait_inside_period(self.obj, period_name))

    async def wait_outside_period(self, period_name: str):
        return await asyncio.create_task(AsyncGear.wait_outside_period(self.obj, period_name))

    async def wait_enter_period(self, period_name: str):
        return await asyncio.create_task(AsyncGear.wait_enter_period(self.obj, period_name))

    async def wait_exit_period(self, period_name: str):
        return await asyncio.create_task(AsyncGear.wait_exit_period(self.obj, period_name))
