# AsyncGear

Think about such a scene, some object has different states or periods, well we call periods. Among these periods, there
can be only one that could be the present period. For example, a human can only be in one period among baby, youth, adult,
old man and dead.

So now not only can you get the exact period, but also await inside the period, await outside the period, await the
instant when the object enters the period and await the instant when the object exits the period.

Remember to distribute different periods for one object.

## uvloop is highly recommended!


### tip
For convince, remember that the python codes below are extracted from this wrapper:

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

### [Install](#Install) · [Usage](#Usage) ·

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

Gear is the core usage, which provides an interface for an object to manipulate the bounded gear.

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
### Gear(obj).delete
When you no more need a gear, you'd better delete it. Especially when you dynamically keep creating new gears, you must keep
deleting the old gears.
```python
Gear('Tom').add_periods('sleep', 'awaken') 
Gear('Tom').delete()
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

'queue blocking' is talked later.
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
You can understand 'run_when_outside' according to ['run_when_inside'](#run_when_inside)

### when_enter
This decorator is similar to run_when_enter. However it is used in class definition.

#### decorate instance method
```python
class C:
    def __init__(self):
        Gear(self).add_periods('sleep', 'awaken')

    @when_enter('awaken')
    def f(self):
        print('synchronous enter awaken callback')

    @when_enter('awaken')
    async def f1(self):
        print('Asynchronous enter awaken callback')

    @when_enter('sleep')
    def f2(self):
        print('synchronous enter sleep callback')

c = C()
await asyncio.create_task(Gear(c).set_period('awaken'))
await asyncio.sleep(1)
await asyncio.create_task(Gear(c).set_period('sleep'))
loop.stop()
```
Result
```shell
synchronous enter awaken callback
Asynchronous enter awaken callback
2021-01-05 18:23:43.974 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set <__main__.main.<locals>.C object at 0x7fcedae93350> to period sleep.
2021-01-05 18:23:43.974 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set <__main__.main.<locals>.C object at 0x7fcedae93350> to period awaken.
2021-01-05 18:23:43.975 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set <__main__.main.<locals>.C object at 0x7fcedae93350> to period awaken.
2021-01-05 18:23:44.976 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set <__main__.main.<locals>.C object at 0x7fcedae93350> to period sleep.
2021-01-05 18:23:44.976 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set <__main__.main.<locals>.C object at 0x7fcedae93350> to period sleep.
synchronous enter sleep callback
```
#### decorate class method
```python
class C:
    @when_enter('awaken')
    @classmethod
    def f(cls):
        print('synchronous enter awaken callback')

    @when_enter('awaken')
    @classmethod
    async def f1(cls):
        print('asynchronous enter awaken callback')

    @when_enter('sleep')
    @classmethod
    def f2(cls):
        print('synchronous enter sleep callback')

Gear(C).add_periods('sleep', 'awaken')
await asyncio.create_task(Gear(C).set_period('awaken'))
await asyncio.sleep(1)
await asyncio.create_task(Gear(C).set_period('sleep'))

loop.stop()
```
Result
```shell
synchronous enter awaken callback
asynchronous enter awaken callback
2021-01-05 18:29:28.379 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set <class '__main__.main.<locals>.C'> to period sleep.
2021-01-05 18:29:28.380 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set <class '__main__.main.<locals>.C'> to period awaken.
2021-01-05 18:29:28.380 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set <class '__main__.main.<locals>.C'> to period awaken.
synchronous enter sleep callback
2021-01-05 18:29:29.383 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set <class '__main__.main.<locals>.C'> to period sleep.
2021-01-05 18:29:29.383 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set <class '__main__.main.<locals>.C'> to period sleep.
```
### when_exit
You can understand according to ['when_enter'](#when_enter)
### when_inside
This decorator is similar to run_when_inside. However it is used in class definition.
```python
class C:
    def __init__(self):
        Gear(self).add_periods('sleep', 'awaken')

    @when_inside('awaken')
    async def f1(self):
        await asyncio.create_task(asyncio.sleep(1))
        print('Aynchronous inside awaken callback')

c = C()
await asyncio.create_task(Gear(c).set_period('awaken'))
await asyncio.create_task(asyncio.sleep(2.5))
await asyncio.create_task(Gear(c).set_period('sleep'))
await asyncio.create_task(asyncio.sleep(1))

loop.stop()
```
Result
```shell
2021-01-06 13:40:15.688 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set <__main__.main.<locals>.C object at 0x7faba315e450> to period sleep.
2021-01-06 13:40:15.689 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set <__main__.main.<locals>.C object at 0x7faba315e450> to period awaken.
2021-01-06 13:40:15.689 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set <__main__.main.<locals>.C object at 0x7faba315e450> to period awaken.
Aynchronous inside awaken callback
Aynchronous inside awaken callback
2021-01-06 13:40:18.192 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set <__main__.main.<locals>.C object at 0x7faba315e450> to period sleep.
2021-01-06 13:40:18.193 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set <__main__.main.<locals>.C object at 0x7faba315e450> to period sleep.
Aynchronous inside awaken callback
```
### when_outside
You can understand according to ['when_inside'](#when_inside)
### high level parameters
#### queue blocking
Decorators below have an optional parameter queue_blocking for the asynchronous decorated functions:
```python
run_when_enter, run_when_exit, when_enter, when_exit
```
'queue_blocking' is to decide the style to run the decorated when the condition is high frequently awaited. For example:
```python
@run_when_enter('Tom', 'awaken')
async def enter_test():
    await asyncio.create_task(asyncio.sleep(0.1))
    print('enter')

Gear('Tom').add_periods('sleep', 'awaken')
await asyncio.create_task(Gear('Tom').set_period('awaken'))
await asyncio.create_task(Gear('Tom').set_period('sleep'))
await asyncio.create_task(Gear('Tom').set_period('awaken'))
await asyncio.create_task(Gear('Tom').set_period('sleep'))
await asyncio.sleep(1)
loop.stop()
```
Result
```shell
2021-01-05 18:53:05.436 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period sleep.
2021-01-05 18:53:05.437 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period awaken.
2021-01-05 18:53:05.437 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period awaken.
2021-01-05 18:53:05.437 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period sleep.
2021-01-05 18:53:05.437 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period sleep.
2021-01-05 18:53:05.438 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period awaken.
2021-01-05 18:53:05.438 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period awaken.
2021-01-05 18:53:05.438 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period sleep.
2021-01-05 18:53:05.439 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period sleep.
enter
```
We high frequently set 'Tom' to enter 'awaken', so enter_test was high frequently run for twice. 
But why we got only one 'enter' printed?

This is because run_when_enter parameter queue_blocking is set to 'abandon' as default, which means abandoning the new activated if the 
previous one has not completed yet.

If it is set to 'non_block':
```python
@run_when_enter('Tom', 'awaken', queue_blocking='non_block')
async def enter_test():
    await asyncio.create_task(asyncio.sleep(0.1))
    print('enter')

Gear('Tom').add_periods('sleep', 'awaken')
await asyncio.create_task(Gear('Tom').set_period('awaken'))
await asyncio.create_task(Gear('Tom').set_period('sleep'))
await asyncio.create_task(Gear('Tom').set_period('awaken'))
await asyncio.create_task(Gear('Tom').set_period('sleep'))
await asyncio.sleep(1)
loop.stop()
```
Result
```shell
2021-01-05 19:01:21.706 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period sleep.
2021-01-05 19:01:21.706 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period awaken.
2021-01-05 19:01:21.707 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period awaken.
2021-01-05 19:01:21.707 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period sleep.
2021-01-05 19:01:21.707 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period sleep.
2021-01-05 19:01:21.708 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period awaken.
2021-01-05 19:01:21.708 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period awaken.
2021-01-05 19:01:21.709 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period sleep.
2021-01-05 19:01:21.709 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period sleep.
enter
enter
```
The two 'enter' were printed at the same time, because the twice enter_test run is non-block.

If it is set to 'queue':
```python
@run_when_enter('Tom', 'awaken', queue_blocking='queue')
async def enter_test():
    await asyncio.create_task(asyncio.sleep(0.1))
    print('enter')

Gear('Tom').add_periods('sleep', 'awaken')
await asyncio.create_task(Gear('Tom').set_period('awaken'))
await asyncio.create_task(Gear('Tom').set_period('sleep'))
await asyncio.create_task(Gear('Tom').set_period('awaken'))
await asyncio.create_task(Gear('Tom').set_period('sleep'))
await asyncio.sleep(1)
loop.stop()
```
Result
```shell
2021-01-05 19:04:03.460 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period sleep.
2021-01-05 19:04:03.461 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period awaken.
2021-01-05 19:04:03.461 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period awaken.
2021-01-05 19:04:03.462 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period sleep.
2021-01-05 19:04:03.462 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period sleep.
2021-01-05 19:04:03.463 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period awaken.
2021-01-05 19:04:03.463 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period awaken.
2021-01-05 19:04:03.464 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period sleep.
2021-01-05 19:04:03.464 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period sleep.
enter
enter
```
The two 'enter' were printed one by one, because among the twice enter_test the latter is blocked by the former but 
enqueued to wait to run.
#### slot_num
```python
Gear(obj).set_period
```
has a parameter -- slot_num.

*Attention! Do not use it before you do understand the parameter!* 

This parameter is used in such a scene, object 'Tom' enters 'sleep' activating 2 friends to be ready to call him 'awaken'
9 hours later. So 9 hours later, 'Tom' would have to be set twice to 'awaken' then could really be awaken. It's hard to 
awake him, haha. 

slot_num means that only after slot_num times Gear(obj)
.set_period(period_name,slot_num) call with the same parameters, the period of Gear(obj) could really be set to 
period_name, which is interrupted 
if among these times set_period run, the same period_name with a different slot_num is given. Then the procedure for 
period_name is refreshed, the count would be reset. For demostration:
```python
Gear('Tom').add_periods('sleep', 'awaken')
await asyncio.create_task(Gear('Tom').set_period('awaken', slot_num=2))
print(Gear('Tom').get_present_period())
await asyncio.create_task(Gear('Tom').set_period('awaken', slot_num=2))
print(Gear('Tom').get_present_period())
loop.stop()
```
Result
```shell
sleep
awaken
2021-01-05 19:18:36.340 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period sleep.
2021-01-05 19:18:36.341 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period awaken.
2021-01-05 19:18:36.341 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period awaken.
```
See? Twice 'set_period' set period to 'awaken' finally.
```python
Gear('Tom').add_periods('sleep', 'awaken')
await asyncio.create_task(Gear('Tom').set_period('awaken', slot_num=2))
print(Gear('Tom').get_present_period())
await asyncio.create_task(Gear('Tom').set_period('awaken', slot_num=3))
print(Gear('Tom').get_present_period())
await asyncio.create_task(Gear('Tom').set_period('awaken', slot_num=3))
print(Gear('Tom').get_present_period())
await asyncio.create_task(Gear('Tom').set_period('awaken', slot_num=3))
print(Gear('Tom').get_present_period())
loop.stop()
```
Result
```shell
sleep
sleep
sleep
awaken
2021-01-05 19:21:32.711 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period sleep.
2021-01-05 19:21:32.713 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period awaken.
2021-01-05 19:21:32.713 | DEBUG    | AsyncGear.AsyncGear:_set_obj_period:74 - set 'Tom' to period awaken.
```
'slot_num=2' is interrupted and the count is reset.
