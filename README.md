# AsyncGear

Think about such a scene, some object has different states or periods, well we call periods. Among these periods, there
can be only one that could be the present period. For example, a human can only be one period among baby, youth, adult,
old man and dead.

So now not only can you get the exact period, but also await inside the period, await outside the period, await the
instance when the object enters the period and await the instance when the object exits the period.

Remember to distribute different periods for one object.

## uvloop is highly recommended!

### [Install](#Install) · [Usage](#Usage) ·

### tip
For convince, remember that the codes below are extracted from this wrapper:

```python
import asyncio
# As recommend, use uvloop
import uvloop

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
from AsyncGear import Gear, run_when_enter, run_when_exit, run_when_inside, run_when_outside, when_enter, when_exit, when_inside, when_outside


async def main():
    # This is the place where these codes are extracted away.
    pass


loop = asyncio.get_event_loop()
loop.create_task(main())
loop.run_forever()
# clear
to_cancel = asyncio.all_tasks(loop)
for task in to_cancel:
    task.cancel()
loop.run_until_complete(
    asyncio.gather(*to_cancel, return_exceptions=True)
)
loop.run_until_complete(loop.shutdown_asyncgens())
```

So if you want to run these codes, you must wrap them back respectively.

Or if you are familiar with asyncio REPL(type 'python -m asyncio' in terminal for python3.8 and above), you can migrate
these codes to run in a terminal line by line.
---

## Install

[AsyncGear in **PyPI**](https://pypi.org/project/AsyncGear/)

```shell
pip install AsyncGear
```

Use in a coroutine.

```python
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
```
Result
```shell
2021-01-05 17:19:20.168 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period sleep.
awaken
2021-01-05 17:19:20.271 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period awaken.
2021-01-05 17:19:20.272 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period awaken.
```
You can also clone it into your project directory
from [AsyncGear GitHub repository](https://github.com/monk-after-90s/AsyncGear.git):

```shell
git clone https://github.com/monk-after-90s/AsyncGear.git
```

---

## Usage

This module provides methods as follows:

```python
from AsyncGear import Gear, run_when_enter, run_when_exit, run_when_inside, run_when_outside, when_enter, when_exit, when_inside, when_outside
```


### Gear

Gear is the basic usage, which provides an interface for an object to manipulate the bounded gear.

```python
# to be simple, the target object is a string
Gear('Tom').add_periods('sleep', 'awaken')  # the first added period would be the default.
Gear('Tom').add_periods('sleepwalking')  # add_periods could be dynamic.
# show the present period.
print(Gear('Tom').get_present_period())
# show all possible periods
print(Gear('Tom').get_period_names())

# beforehand wait the target time of the target period
async def wait_enter(gear: Gear, period):
    await asyncio.create_task(gear.wait_enter_period(period))
    print(f'enter {period}')

asyncio.create_task(wait_enter(Gear('Tom'), 'awaken'))

async def wait_exit(gear: Gear, period):
    await asyncio.create_task(gear.wait_exit_period(period))
    print(f'exit {period}')

asyncio.create_task(wait_exit(Gear('Tom'), 'sleep'))

async def wait_outside(gear: Gear, period):
    while True:
        await asyncio.create_task(gear.wait_outside_period(period))
        await asyncio.sleep(0.3)
        print(f'outside {period}')

asyncio.create_task(wait_outside(Gear('Tom'), 'sleep'))

async def wait_inside(gear: Gear, period):
    while True:
        await asyncio.create_task(gear.wait_inside_period(period))
        await asyncio.sleep(0.3)
        print(f'inside {period}')

asyncio.create_task(wait_inside(Gear('Tom'), 'awaken'))
await asyncio.create_task(Gear('Tom').set_period('awaken'))
# stay in awaken for 1 seconds
await asyncio.sleep(1)
loop.stop()
```
Result
```shell
2021-01-05 17:15:23.600 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period sleep.
2021-01-05 17:15:23.601 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period awaken.
2021-01-05 17:15:23.601 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period awaken.
2021-01-05 17:15:23.601 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period awaken.
sleep
dict_keys(['sleep', 'awaken', 'sleepwalking'])
exit sleep
enter awaken
outside sleep
inside awaken
outside sleep
inside awaken
outside sleep
inside awaken
```
### run_when_enter
run_when_enter is to decorate a function or coroutine function to be run when just entering the designated period of 
the designated object gear.
```python
Gear('Tom').add_periods('sleep', 'awaken')

@run_when_enter('Tom', 'awaken')
def enter_test():
    print('synchronous callback')

@run_when_enter('Tom', 'awaken')
async def async_enter_test():
    print('asynchronous callback')

await asyncio.create_task(Gear('Tom').set_period('awaken'))

loop.stop()
```
Result
```shell
synchronous callback
asynchronous callback
2021-01-05 17:20:34.636 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period sleep.
2021-01-05 17:20:34.636 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period awaken.
2021-01-05 17:20:34.636 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period awaken.
```
### run_when_exit
run_when_exit is to decorate a function or coroutine function to be run when just exiting the designated period of 
the designated object gear.
```python
Gear('Tom').add_periods('sleep', 'awaken')

@run_when_exit('Tom', 'sleep')
def enter_test():
    print('synchronous callback')

@run_when_exit('Tom', 'sleep')
async def async_enter_test():
    print('asynchronous callback')

await asyncio.create_task(Gear('Tom').set_period('awaken'))

loop.stop()
```
Result
```shell
synchronous callback
asynchronous callback
2021-01-05 17:23:13.993 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period sleep.
2021-01-05 17:23:13.994 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period awaken.
2021-01-05 17:23:13.994 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period awaken.
```
### run_when_inside
run_when_inside is to decorate a function or coroutine function to be run when being inside the designated period of 
the designated object gear.

Logically, 'inside' is a time slot, so the condition is frequently awaited and the decorated is frequently run. To make 
sense, this must not happen. Therefore we set a 'queue blocking' style -- 'abandon', which means abandoning the new activated if the 
previous one has not completed yet.
```python
Gear('Tom').add_periods('sleep', 'awaken')

@run_when_inside('Tom', 'awaken')
async def inside_test():
    await asyncio.create_task(asyncio.sleep(1))
    print(f'inside awaken')

await asyncio.create_task(Gear('Tom').set_period('awaken'))
await asyncio.create_task(asyncio.sleep(2.5))
await asyncio.create_task(Gear('Tom').set_period('sleep'))
await asyncio.create_task(asyncio.sleep(1))
loop.stop()
```
Result
```shell
2021-01-05 17:38:29.518 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period sleep.
2021-01-05 17:38:29.519 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period awaken.
2021-01-05 17:38:29.519 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period awaken.
inside awaken
inside awaken
2021-01-05 17:38:32.021 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period sleep.
2021-01-05 17:38:32.021 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period sleep.
inside awaken
```
See? In 2.5 seconds, there could be only 3 inside_test run and when the period was set 
to 'sleep' the last inside_test had not completed yet.
### run_when_outside
You can 'run_when_outside' according to ['run_when_inside'](#run_when_inside)