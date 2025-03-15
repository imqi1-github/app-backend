from functools import wraps


def print_blanks(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        print("\n" + "-" * 10)
        result = func(*args, **kwargs)
        print("-" * 10, "\n")
        return result

    return decorator
