call_backs = {}


def _when_ins(time_method: str, period_name: str, queue_blocking='abandon'):
    '''
    remenber to instantiate in a coroutine

    :param period_name:
    :param queue_blocking: When the decorated is activated too frequently, 'non_block' means run immediately anyway; 'queue' means
                             waits the previous one completing then run the new activated; 'abandon' means abandon the new
                             activated if the previous one has not completed yet.
    :return:
    '''

    def decorator(f):
        call_backs[getattr(f, '__func__', f) if type(f) is classmethod else f] = \
            call_backs.get(getattr(f, '__func__', f) if type(f) is classmethod else f, {})
        call_backs[getattr(f, '__func__', f) if type(f) is classmethod else f][period_name] = \
            call_backs[getattr(f, '__func__', f) if type(f) is classmethod else f].get(period_name, {})
        call_backs[getattr(f, '__func__', f) if type(f) is classmethod else f][period_name][time_method] = \
            queue_blocking
        return f

    return decorator


def when_enter(period_name: str, queue_blocking='abandon'):
    '''
    Decorate a class method or its instance method, to be run when the class or the instance gear enters period
    period_name. You can set the gear periods later. Remember to use in a coroutine.

    :param period_name:
    :param queue_blocking: When the decorated is activated too frequently, 'non_block' means run immediately anyway; 'queue' means
                             waits the previous one completing then run the new activated; 'abandon' means abandon the new
                             activated if the previous one has not completed yet.
    :return:
    '''
    return _when_ins('enter', period_name, queue_blocking)


def when_exit(period_name: str, queue_blocking='abandon'):
    '''
    Decorate a class method or its instance method, to be run when the class or the instance gear exits period
    period_name. You can set the gear periods later. Remember to use in a coroutine.

    :param period_name:
    :param queue_blocking: When the decorated is activated too frequently, 'non_block' means run immediately anyway; 'queue' means
                             waits the previous one completing then run the new activated; 'abandon' means abandon the new
                             activated if the previous one has not completed yet.
    :return:
    '''
    return _when_ins('exit', period_name, queue_blocking)


def when_inside(period_name: str, ):
    '''
    Decorate a class method or its instance method, to be run when the class or the instance gear is inside period
    period_name. You can set the gear periods later. Remember to use in a coroutine.

    :param period_name:
    :return:
    '''
    return _when_ins('inside', period_name, 'abandon')


def when_outside(period_name: str, ):
    '''
    Decorate a class method or its instance method, to be run when the class or the instance gear is outside period
    period_name. You can set the gear periods later. Remember to use in a coroutine.

    :param period_name:
    :return:
    '''
    return _when_ins('outside', period_name, 'abandon')
