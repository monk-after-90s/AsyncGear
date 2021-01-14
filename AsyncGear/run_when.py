import asyncio


def _run_when(obj, time_method: str, period_name: str, queue_blocking='abandon'):
    '''
    Decorator, run the decorated when obj is at the exact moment or period.

    :param time_method: enter, exit, inside, outside
    :param obj:
    :param period_name:
    :param queue_blocking: When the decorated is activated too frequently, non_block means run immediately anyway; queue means
                             waits the previous one completing then run the new activated; abandon means abandon the new
                             activated if the previous one has not completes yet.
    :return:
    '''

    def decrator(decorated):
        async def runner():
            if asyncio.iscoroutinefunction(decorated):
                if queue_blocking == 'abandon':
                    pending_task: asyncio.Task = None
                elif queue_blocking == 'queue':
                    q = asyncio.Queue()

                    # Get q item to run decorated
                    async def queue2run_coroutine():
                        while True:
                            await asyncio.create_task(q.get())
                            await asyncio.create_task(decorated())
                            q.task_done()

                    asyncio.create_task(queue2run_coroutine())
            while True:
                # wait the exact time
                from .Gear import Gear
                await asyncio.create_task(getattr(Gear(obj),
                                                  {'enter': 'wait_enter_period',
                                                   'exit': 'wait_exit_period',
                                                   'inside': 'wait_inside_period',
                                                   'outside': 'wait_outside_period'}[time_method])(period_name))
                if not asyncio.iscoroutinefunction(decorated):
                    decorated()
                else:
                    if queue_blocking == 'non_block':
                        asyncio.create_task(decorated())
                    elif queue_blocking == 'abandon':
                        if not bool(pending_task) or pending_task.done():  # previous completes
                            pending_task = asyncio.create_task(decorated())
                        elif bool(pending_task):
                            await pending_task
                    elif queue_blocking == 'queue':
                        q.put_nowait(None)

        runner_task = asyncio.create_task(runner())
        from .Gear import Gear
        Gear(obj).assistant_tasks.append(runner_task)

        return decorated

    return decrator


def run_when_enter(obj, period_name: str, queue_blocking='abandon'):
    '''
    Decorator, run the decorated when obj enters the period.

    :param obj:
    :param period_name:
    :param queue_blocking: When the decorated is activated too frequently, 'non_block' means run immediately anyway; 'queue' means
                             waits the previous one completing then run the new activated; 'abandon' means abandon the new
                             activated if the previous one has not completed yet.
    :return:
    '''
    return _run_when(obj, 'enter', period_name, queue_blocking)


def run_when_exit(obj, period_name: str, queue_blocking='abandon'):
    '''
    Decorator, run the decorated when obj exits the period.

    :param obj:
    :param period_name:
    :param queue_blocking: When the decorated is activated too frequently, 'non_block' means run immediately anyway; 'queue' means
                             waits the previous one completing then run the new activated; 'abandon' means abandon the new
                             activated if the previous one has not completed yet.
    :return:
    '''
    return _run_when(obj, 'exit', period_name, queue_blocking)


def run_when_inside(obj, period_name: str):
    '''
    Decorator, run the decorated when obj is inside the period. The queue blocking style is 'abandon', which means abandon the new
    activated if the previous one has not completed yet.

    :param obj:
    :param period_name:
    :return:
    '''
    return _run_when(obj, 'inside', period_name, 'abandon')


def run_when_outside(obj, period_name: str):
    '''
    Decorator, run the decorated when obj is outside the period. The queue blocking style is 'abandon', which means abandon the new
    activated if the previous one has not completed yet.

    :param obj:
    :param period_name:
    :return:
    '''
    return _run_when(obj, 'outside', period_name, 'abandon')
