# AsyncGear

Think about such a scene, some object has different states or periods, well we call periods. Among these periods, there
can be only one that could be the present period. For example, a human can only be one period among baby, youth, adult,
old man and dead.

So now not only can you get the exact period, but also await inside the period, await outside the period, await the
instance when the object enters the period and await the instance when the object exits the period.

Remember to distribute different periods for one object.

## uvloop is highly recommended!

### [Install](#Install) · [Usage](#Usage) ·

---

## Install

[AsyncGear in **PyPI**](https://pypi.org/project/AsyncGear/)

```shell
pip install AsyncGear
```

Use in a coroutine.

```python
import asyncio
# As recommend, use uvloop
import uvloop

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
from AsyncGear import Gear


async def main():
    Gear('Tom').add_periods('sleep', 'awaken')

    async def wait_awaken():
        await asyncio.create_task(Gear('Tom').wait_enter_period('awaken'))
        print('awaken')
        # When all tasks completed, close the loop.
        loop.stop()

    # set up a task to wait period 'awaken'
    asyncio.create_task(wait_awaken())
    # sleep for a while
    await asyncio.create_task(asyncio.sleep(0.1))
    # set the period
    await asyncio.create_task(Gear('Tom').set_period('awaken'))


loop = asyncio.get_event_loop()
loop.create_task(main())
loop.run_forever()
```

You can also clone it into your project directory
from [AsyncGear GitHub repository](https://github.com/monk-after-90s/AsyncGear.git):

```shell
git clone https://github.com/monk-after-90s/AsyncGear.git
```

---

## Usage