import time
import functools

def rate_limited(max_per_minute):
    """
    Decorator to limit the rate of function calls.
    
    Args:
        max_per_minute: The maximum number of calls allowed per minute.
    """
    min_interval = 15 / max_per_minute

    def decorate(func):
        last_time_called = 0

        @functools.wraps(func)
        def rate_limited_function(*args, **kwargs):
            nonlocal last_time_called
            elapsed = time.monotonic() - last_time_called
            left_to_wait = min_interval - elapsed

            if left_to_wait > 0:
                time.sleep(left_to_wait)

            last_time_called = time.monotonic()
            return func(*args, **kwargs)

        return rate_limited_function

    return decorate