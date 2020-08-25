import asyncio


# todo 以后可以想想实现子集、并集、交集等，最小元素考虑是互斥时期

class AsyncExclusivePeriod:
    obj_has_async_exclusive_periods = {}

    @classmethod
    async def create_obj_periods(cls, obj, *period_names: str):
        '''
        Initially create periods for some object.

        :param obj:
        :param period_names: Period names.The first one would be the initial period.
        :return:
        '''
        if obj not in cls.obj_has_async_exclusive_periods.keys():
            cls.obj_has_async_exclusive_periods[obj] = cls.obj_has_async_exclusive_periods.get(obj, {})
            for period_name in period_names:
                cls.obj_has_async_exclusive_periods[obj][period_name] = AsyncExclusivePeriod(period_name)
            await cls.set_obj_period(obj, period_names[0])
        else:
            raise KeyError(f'{repr(obj)} has already got some periods! Please use add_period.')

    @classmethod
    async def add_period(cls, obj, new_period_name: str):
        '''
        Dynamically add a period for some object.

        :return:
        '''
        if obj not in cls.obj_has_async_exclusive_periods.keys():
            await cls.create_obj_periods(obj, new_period_name)
        else:
            cls.obj_has_async_exclusive_periods[obj][new_period_name] = AsyncExclusivePeriod(new_period_name)

    @classmethod
    def _get_obj_period(cls, obj, period_name: str):
        if obj in cls.obj_has_async_exclusive_periods.keys() and \
                period_name in cls.obj_has_async_exclusive_periods[obj].keys():
            return cls.obj_has_async_exclusive_periods[obj][period_name]
        else:
            raise KeyError(f'You did not create {period_name} for {repr(obj)}!')

    @classmethod
    def get_obj_present_period(cls, obj):
        for name, period in cls._get_obj_periods(obj).items():
            if period._get_state():
                return name

    @classmethod
    def get_obj_period_names(cls, obj):
        if obj in cls.obj_has_async_exclusive_periods.keys():
            return cls.obj_has_async_exclusive_periods[obj].keys()
        else:
            raise KeyError(f'You did not create any AsyncExclusivePeriod for {repr(obj)}!')

    @classmethod
    def _get_obj_periods(cls, obj):
        if obj in cls.obj_has_async_exclusive_periods.keys():
            return cls.obj_has_async_exclusive_periods[obj]

    @classmethod
    async def set_obj_period(cls, obj, period_name: str):
        _ensure_state_tasks = []
        for name, period in cls._get_obj_periods(obj).items():
            # 目标
            if name == period_name:
                _ensure_state_tasks.append(asyncio.create_task(period._ensure_state(True)))
            else:
                _ensure_state_tasks.append(asyncio.create_task(period._ensure_state(False)))
        [await task for task in _ensure_state_tasks]

    @classmethod
    async def wait_inside_period(cls, obj, period_name: str):
        period: cls = cls._get_obj_period(obj, period_name)
        await period._wait_true()

    @classmethod
    async def wait_outside_period(cls, obj, period_name: str):
        period: cls = cls._get_obj_period(obj, period_name)
        await period._wait_false()

    @classmethod
    async def wait_enter_period(cls, obj, period_name: str):
        period: cls = cls._get_obj_period(obj, period_name)
        await period._wait_change_into_true()

    @classmethod
    async def wait_exit_period(cls, obj, period_name: str):
        period: cls = cls._get_obj_period(obj, period_name)
        await period._wait_change_into_false()

    def __init__(self, name):
        self._enter_event = asyncio.Event()
        self._exit_event = asyncio.Event()
        self._name = name

    async def _ensure_state(self, state: bool):
        if state:
            if not self._enter_event.is_set():
                self._enter_event.set()
                await asyncio.sleep(0)
            if self._exit_event.is_set():
                self._exit_event.clear()
        else:
            if self._enter_event.is_set():
                self._enter_event.clear()
            if not self._exit_event.is_set():
                self._exit_event.set()
                await asyncio.sleep(0)

    def _get_state(self):
        return self._enter_event.is_set() and not self._exit_event.is_set()

    async def _wait_true(self):
        await self._enter_event.wait()

    async def _wait_false(self):
        await self._exit_event.wait()

    async def _wait_change_into_true(self):
        if self._get_state():
            await self._wait_false()
            await self._wait_true()
        else:
            await self._wait_true()

    async def _wait_change_into_false(self):
        if self._get_state():
            await self._wait_false()
        else:
            await self._wait_true()
            await self._wait_false()
