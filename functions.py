from beaker.cache import CacheManager, cache_region
from beaker.util import parse_cache_config_options

from functools import wraps


def CustomCache():
    cache_opts = {
        'cache.type': 'file',
        'cache.data_dir': '/tmp/cache/data',
        #'cache.lock_dir': '/tmp/cache/lock',
        'cache.regions': 'short_term, long_term',
        'cache.long_term.type': 'file',
        'cache.long_term.expire': '86400',
        }
    return CacheManager(**parse_cache_config_options(cache_opts))


def mycache(func):
    cache = CustomCache()
    name = hash(func.__code__)
    @wraps(func)
    @cache_region('long_term', name)
    def wrapper(*args, **kwds):
         return func(*args, **kwds)
    return wrapper

def mysmartcache(func):
    cache = CustomCache()
    name = func.__name__
    # See if key exists
    print('%s new.'%(name))
    @wraps(func)
    @cache_region('long_term', name)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@mycache
def funcA(x):
    '''Docstring'''
    print('funcA(%s) called'%(x))
    return x

@mycache
def funcB(x):
    return 2*x

if __name__=='__main__':
    print(funcA(4))
    print(funcA(3))
    print(funcB(7))
