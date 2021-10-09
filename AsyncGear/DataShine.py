import asyncio

from .Gear import _Gear


class DataShine(_Gear):
    def __init__(self):
        super(DataShine, self).__init__(self)
        self._data = None
        self.add_periods('shine', 'slake')
        self._q = asyncio.Queue(10)
        self._data_scheduler_task: asyncio.Task = asyncio.create_task(self._data_scheduler())

    async def _data_scheduler(self):
        while True:
            self._data = await self._q.get()
            self._q.task_done()
            if self.get_present_period() != 'shine':
                await self.set_period('shine')
            else:
                await self.set_period('slake')

    async def push_data(self, data):
        '''
        Set the lamp to carry a data to be taken, and shine the data to notify monitors new data coming.

        :param data:
        :return:
        '''
        await asyncio.create_task(self._q.put(data))

    @property
    def data(self):
        '''
        Query the data last pushed.

        :return:
        '''
        return self._data

    async def wait_data_shine(self):
        '''
        Wait the shined data. If you wait too later, you will lose the chance to get the data. If you can not wait the data
        in time every time but have to handle all the data, you can cache data in a instance of asyncio.Queue.

        All monitors share the same data reference, thus if it is mutable and modified, all data will be change. For example,
        monitor1 and monitor2 get data [1], and monitor1 modifies it to [2], monitor2 will find its data is changed to [2], too.
        You can use 'deepcopy' to aviod this situation.

        :return:
        '''
        if self.get_present_period() != 'shine':
            await asyncio.create_task(self.wait_enter_period('shine'))
        else:
            await asyncio.create_task(self.wait_enter_period('slake'))
        return self._data
