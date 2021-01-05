'''
Transfer an object to its gear, as an interface.
'''
import asyncio

from .AsyncGear import AsyncGear

from .method_run_when import call_backs


class Gear:
    # last_set_period = {}

    def __init__(self, obj):
        self.obj = obj

    def _set_intance_gear_callbacks(self, period_names):
        def _set_intance_gear_callbacks(attr, obj, period_names):
            from .run_when import _run_when
            periods2del = []
            for period_name in period_names:  # 新时期被加入，找到可以启动的回调等待
                if period_name in call_backs[attr].keys():  # 启动等待
                    periods2del.append(period_name)
                    for time_method in call_backs[attr][period_name].keys():
                        if asyncio.iscoroutinefunction(attr):
                            @_run_when(obj, time_method, period_name, call_backs[attr][period_name][time_method])
                            async def wrapper():
                                await asyncio.create_task(attr(obj))
                        else:
                            @_run_when(obj, time_method, period_name, call_backs[attr][period_name][time_method])
                            def wrapper():
                                # print(f'attr:{repr(attr)}')
                                attr(obj)

            # 删除该period记录
            [call_backs[attr].pop(period) for period in periods2del]
            # 如果attr没有还要关联的period，则删除该attr的记录
            if not bool(call_backs[attr]):
                call_backs.pop(attr)

        for attr in set(getattr(type(self.obj), '__dict__', {}).values()) | \
                    set(getattr(self.obj, '__dict__', {}).values()):  # 遍历绑定对象的命名空间及其类命名空间，找到实例回调方法对应的类函数
            attr = getattr(attr, '__func__', attr) if type(attr) is classmethod else attr
            if attr in call_backs:
                _set_intance_gear_callbacks(attr, self.obj, period_names)

    def add_periods(self, *new_period_names: str):
        '''
        Dynamically add periods for some object. The first added would be the default.

        :return:
        '''
        for new_period_name in new_period_names:
            AsyncGear.add_period(self.obj, new_period_name)
        self._set_intance_gear_callbacks(new_period_names)

    def get_present_period(self):
        '''
        Get the present period of the target object.

        :return:
        '''
        return AsyncGear.get_obj_present_period(self.obj)

    def get_period_names(self):
        '''
        Get the periods of the target object.

        :return:
        '''
        return AsyncGear.get_obj_period_names(self.obj)

    async def set_period(self, period_name: str, slot_num: int = 1):
        '''
        Set obj to period period_name.

        :param period_name:
        :param slot_num: Attention! Do not use it if you do not understand the parameter!
                slot_num means that only after slot_num times Gear(obj).set_period(period_name,slot_num) run,
                the period of Gear(obj) could really be set to period_name, which is interrupted
                if among these times set_period run, the same period_name with a different slot_num is given.
                Then the procedure is refreshed, the count would be reset.
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
        '''
        Wait the time slot when the gear is inside period period_name. As logically, as long as the gear is inside period
        period_name, this coroutine is awaited immediately.

        :param period_name:
        :return:
        '''
        return await asyncio.create_task(AsyncGear.wait_inside_period(self.obj, period_name))

    async def wait_outside_period(self, period_name: str):
        '''
        Wait the time slot when the gear is outside period period_name. As logically, as long as the gear is outside period
        period_name, this coroutine is awaited immediately.

        :param period_name:
        :return:
        '''
        return await asyncio.create_task(AsyncGear.wait_outside_period(self.obj, period_name))

    async def wait_enter_period(self, period_name: str):
        '''
        Wait the instant when the gear enters period period_name.

        :param period_name:
        :return:
        '''
        return await asyncio.create_task(AsyncGear.wait_enter_period(self.obj, period_name))

    async def wait_exit_period(self, period_name: str):
        '''
        Wait the instant when the gear exits period period_name.

        :param period_name:
        :return:
        '''
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
