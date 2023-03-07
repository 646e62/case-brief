from functools import wraps
from time import time, sleep

def timing(func):
    """A simple timer decorator"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time()
        result = func(*args, **kwargs)
        end = time()
        with open("timings.log", "a") as fh:
            fh.write(f'Elapsed time {func.__name__}: {end - start}\n')
        return result
    return wrapper
