import time
import functools

def retry(times: int = 3, delay: float = 1.0):
    def wrapper(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == times:
                        raise
                    print(f"[retry] {attempt} failed: {e}, retrying...")
                    time.sleep(delay)
        return inner
    return wrapper
