import numpy as np

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