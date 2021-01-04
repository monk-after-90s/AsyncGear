# def class_decorator(some_class):
#     '''
#     :param some_class:
#     :return:
#     '''
# from types import MethodType, FunctionType


# class GearMetaClass(type):
#     pass
#
#
# class C(metaclass=GearMetaClass):
#     gear_periods = []
#
#     def __init__(self):
#         instance_gear_periods = []
# from .AsyncGearInterface import Gear

call_backs = {}


def when_ins_enter(period_name: str, queue_blocking='abandon'):
    '''
    remenber to instantiate in a coroutine

    :param period_name:
    :param queue_blocking: When the decorated is activated too frequently, 'non_block' means run immediately anyway; 'queue' means
                             waits the previous one completing then run the new activated; 'abandon' means abandon the new
                             activated if the previous one has not completed yet.
    :return:
    '''

    def decorator(f):
        # # print(__name__)
        # if __name__ == '__main__':
        #     # 此时全局还没有C
        #     # print(eval(f.__qualname__), )
        #     # print(globals())
        #     pass
        # else:
        #     # exec(f'''import {__name__};{__name__}.__Gear_callbacks__={'{}'}''')
        #     # print(__Gear_callbacks__)
        #     import __main__  # 主启动模块，并非一定是导入该库的模块
        #     __main__.__Gear_callbacks__ = {}
        #     # print(f.__qualname__)

        # return str(f.__qualname__).split('.')[-1]

        # call_backs[f] = call_backs.get(f, {})
        # call_backs[f]['enter'] = 0

        call_backs[f] = call_backs.get(f, {})
        call_backs[f][period_name] = call_backs[f].get(period_name, {})
        call_backs[f][period_name]['enter'] = queue_blocking
        return f

    return decorator
