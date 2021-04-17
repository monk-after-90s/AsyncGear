'''
Transfer an object to its gear, as an interface.
'''
import asyncio
import datetime

from .AsyncPeriod import AsyncPeriod

from .method_run_when import call_backs
from ensureTaskCanceled import ensureTaskCanceled

gears = {}


class _Gear:
    # last_set_period = {}

    def __init__(self, obj):
        self.obj = obj
        self.periods = {}
        self._unlocked = asyncio.Event()
        self._unlocked.set()
        self.assistant_tasks = []
        self.prev_period = None
        self._current_period: AsyncPeriod = None

    def delete(self):
        '''
        Delete the gear. You'd better delete the gear when it is no more used.

        :return:
        '''
        if self.obj in gears.keys():
            gears.pop(self.obj)
        for task in self.assistant_tasks:
            asyncio.create_task(ensureTaskCanceled(task))

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
                                return await asyncio.create_task(attr(obj))
                        else:
                            @_run_when(obj, time_method, period_name, call_backs[attr][period_name][time_method])
                            def wrapper():
                                return attr(obj)

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
            if new_period_name in self.periods.keys():
                raise KeyError(f'Period {new_period_name} has already been added.')
            self.periods[new_period_name] = AsyncPeriod(new_period_name, self.obj, self)
            if len(self.periods.keys()) == 1:
                self._set_period(new_period_name)

        self._set_intance_gear_callbacks(new_period_names)

    def get_present_period(self):
        '''
        Get the present period of the target object.

        :return:
        '''
        if self._current_period is not None:
            return self._current_period._name

    def current_set_datetime(self) -> datetime.datetime:
        '''
        Get the UTC datetime when the present period is set.

        :return:
        '''
        if self._current_period is not None:
            return self._current_period._ensured_time

    def get_period_names(self):
        '''
        Get the periods of the target object.

        :return:
        '''
        return tuple(self.periods.keys())

    def _set_period(self, period_name: str, slot_num: int = 1):
        p = self.periods[period_name]
        p.slots_num_for_true = slot_num
        p.filled_slots_num += 1

    async def set_period(self, period_name: str, slot_num: int = 1):
        '''
        Set obj to period period_name when unlocked, otherwise PermissionError is raised.

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
            if self._unlocked.is_set():
                self._set_period(period_name, slot_num)
            else:
                raise PermissionError('The gear is locked.')
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
        period = self.periods[period_name]
        await asyncio.create_task(period.wait_true())

    async def wait_outside_period(self, period_name: str):
        '''
        Wait the time slot when the gear is outside period period_name. As logically, as long as the gear is outside period
        period_name, this coroutine is awaited immediately.

        :param period_name:
        :return:
        '''
        period = self.periods[period_name]
        await asyncio.create_task(period.wait_false())

    async def wait_enter_period(self, period_name: str):
        '''
        Wait the instant when the gear enters period period_name.

        :param period_name:
        :return:
        '''
        period = self.periods[period_name]
        await asyncio.create_task(period.wait_change_into_true())

    async def wait_exit_period(self, period_name: str):
        '''
        Wait the instant when the gear exits period period_name.

        :param period_name:
        :return:
        '''
        period = self.periods[period_name]
        await asyncio.create_task(period.wait_change_into_false())

    def lock(self):
        '''
        Lock the period of the gear.

        :return:
        '''
        self._unlocked.clear()

    def unlock(self):
        '''
        Unlock the period of the gear after the gear is locked.

        :return:
        '''
        self._unlocked.set()

    async def wait_unlock(self):
        '''
        wait the gear to be unlocked.

        :return:
        '''
        await asyncio.create_task(self._unlocked.wait())
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


def Gear(obj) -> _Gear:
    if obj not in gears.keys():
        gears[obj] = _Gear(obj)
    return gears[obj]
