import inspect
import sys


def get_function_name(frames=1):
    # if frames == 1:
    #     return inspect.currentframe().f_code.co_name
    return sys._getframe(frames).f_code.co_name if hasattr(sys, "_getframe") else None
