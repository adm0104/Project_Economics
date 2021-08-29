import numpy as np
import inspect

def roundup_log(x):
    if x < 1:
        return 1
    else:
        return 10 ** len(str(int(x)))

def roundup_lin(x):
    if x < 1:
        return 1
    else:
        return (3 + x // 10 ** (len(str(int(x)))-1)) * 10 ** (len(str(int(x)))-1)

def retrieve_name(var):
    callers_local_vars = inspect.currentframe().f_back.f_locals.items()
    return [var_name for var_name, var_val in callers_local_vars if var_val is var]