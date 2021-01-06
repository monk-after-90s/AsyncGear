import asyncio

# todo 以后可以想想实现子集、并集、交集等，最小元素考虑是互斥时期
from loguru import logger


class AsyncPeriod:
    def __init__(self, name, obj, gear):
        self._true_event = asyncio.Event()
        self._false_event = asyncio.Event()
        self._ensure_state(False)
        self._name = name
        self.obj = obj
        self.gear = gear

        self._slots_num_for_true = 1
        self._filled_slots_num = 0

    @property
    def slots_num_for_true(self):
        return self._slots_num_for_true

    @slots_num_for_true.setter
    def slots_num_for_true(self, x: int):
        if self._slots_num_for_true != x:  # 更新
            self.filled_slots_num = 0

        self._slots_num_for_true = x

    @property
    def filled_slots_num(self):
        return self._filled_slots_num

    @filled_slots_num.setter
    def filled_slots_num(self, x: int):
        self._filled_slots_num = x
        # 触发
        if self.filled_slots_num >= self.slots_num_for_true:
            for period in self.gear.periods.values():
                period._ensure_state(period is self)

                logger.debug(f'set {repr(self.obj)} to period {self._name}.')

            self.filled_slots_num = 0

    def _ensure_state(self, state: bool):
        if state:
            if not self._true_event.is_set():
                self._true_event.set()
            if self._false_event.is_set():
                self._false_event.clear()

        else:
            if self._true_event.is_set():
                self._true_event.clear()
            if not self._false_event.is_set():
                self._false_event.set()

    def get_state(self):
        return self._true_event.is_set() and not self._false_event.is_set()

    async def wait_true(self):
        await asyncio.create_task(self._true_event.wait())

    async def wait_false(self):
        await asyncio.create_task(self._false_event.wait())

    async def wait_change_into_true(self):
        if self.get_state():
            await asyncio.create_task(self.wait_false())
            await asyncio.create_task(self.wait_true())
        else:
            await asyncio.create_task(self.wait_true())

    async def wait_change_into_false(self):
        if self.get_state():
            await asyncio.create_task(self.wait_false())
        else:
            await asyncio.create_task(self.wait_true())
            await asyncio.create_task(self.wait_false())

    # obj_has_async_exclusive_periods = {}
    #
    # @classmethod
    # def create_obj_periods(cls, obj, *period_names: str):
    #     '''
    #     Initially create periods for some object.
    #
    #     :param obj:
    #     :param period_names: Period names.The first one would be the initial period.
    #     :return:
    #     '''
    #     if obj not in cls.obj_has_async_exclusive_periods.keys():
    #         cls.obj_has_async_exclusive_periods[obj] = cls.obj_has_async_exclusive_periods.get(obj, {})
    #         for period_name in period_names:
    #             cls.obj_has_async_exclusive_periods[obj][period_name] = AsyncGear(period_name, obj)
    #         cls._set_obj_period(obj, period_names[0])
    #     else:
    #         raise KeyError(f'{repr(obj)} has already got some periods! Please use add_period.')
    #
    # @classmethod
    # def add_period(cls, obj, new_period_name: str):
    #     '''
    #     Dynamically add a period for some object.
    #
    #     :return:
    #     '''
    #     if obj not in cls.obj_has_async_exclusive_periods.keys():
    #         cls.create_obj_periods(obj, new_period_name)
    #     else:
    #         cls.obj_has_async_exclusive_periods[obj][new_period_name] = AsyncGear(new_period_name, obj)
    #
    # @classmethod
    # def _get_obj_period(cls, obj, period_name: str):
    #     if obj in cls.obj_has_async_exclusive_periods.keys() and \
    #             period_name in cls.obj_has_async_exclusive_periods[obj].keys():
    #         return cls.obj_has_async_exclusive_periods[obj][period_name]
    #     else:
    #         raise KeyError(f'You did not create {period_name} for {repr(obj)}!')
    #
    # @classmethod
    # def get_obj_present_period(cls, obj):
    #     for name, period in cls._get_obj_periods(obj).items():
    #         if period._get_state():
    #             return name
    #
    # @classmethod
    # def get_obj_period_names(cls, obj):
    #     if obj in cls.obj_has_async_exclusive_periods.keys():
    #         return cls.obj_has_async_exclusive_periods[obj].keys()
    #     else:
    #         raise KeyError(f'You did not create any AsyncGear for {repr(obj)}!')
    #
    # @classmethod
    # def _get_obj_periods(cls, obj):
    #     if obj in cls.obj_has_async_exclusive_periods.keys():
    #         return cls.obj_has_async_exclusive_periods[obj]
    #
    # @classmethod
    # def _set_obj_period(cls, obj, period_name: str):
    #     if cls.get_obj_present_period(obj) != period_name:
    #         for name, period in cls._get_obj_periods(obj).items():
    #             # 目标
    #             if name == period_name:
    #                 period._ensure_state(True)
    #             else:
    #                 period._ensure_state(False)
    #             logger.debug(f'set {repr(obj)} to period {period_name}.')
    #
    # @classmethod
    # async def set_obj_period(cls, obj, period_name: str, slot_num: int = 1):
    #     '''
    #     Set obj to period period_name.
    #
    #     :param obj:
    #     :param period_name:
    #     :param slot_num: Attention! Do not use it if you do not understand it!
    #             slot_num means that only after slot_num times AsyncGear.set_obj_period(obj,period_name,slot_num) run
    #             (present time included), the period of obj gear could really be set to period_name, which is interrupted
    #             if among these times set_obj_period run a different slot_num is given. Then the procedure is refreshed.
    #     :return:
    #     '''
    #     p = cls._get_obj_period(obj, period_name)
    #     p.slots_num_for_true = slot_num
    #     p.filled_slots_num += 1
    #
    #     # cls._set_obj_period(obj, period_name)
    #     # if cls.get_obj_present_period(obj) != period_name:
    #     #     await asyncio.create_task(AsyncGear.wait_outside_period(obj, period_name))
    #     # else:
    #     #     await asyncio.create_task(AsyncGear.wait_inside_period(obj, period_name))
    #     # await asyncio.create_task(AsyncGear.wait_inside_period(obj, period_name))
    #
    # @classmethod
    # async def wait_inside_period(cls, obj, period_name: str):
    #     period: cls = cls._get_obj_period(obj, period_name)
    #     await asyncio.create_task(period._wait_true())
    #
    # @classmethod
    # async def wait_outside_period(cls, obj, period_name: str):
    #     period: cls = cls._get_obj_period(obj, period_name)
    #     await asyncio.create_task(period.wait_false())
    #
    # @classmethod
    # async def wait_enter_period(cls, obj, period_name: str):
    #     period: cls = cls._get_obj_period(obj, period_name)
    #     await asyncio.create_task(period.wait_change_into_true())
    #
    # @classmethod
    # async def wait_exit_period(cls, obj, period_name: str):
    #     period: cls = cls._get_obj_period(obj, period_name)
    #     await asyncio.create_task(period._wait_change_into_false())
