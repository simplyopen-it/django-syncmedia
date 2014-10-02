import os


def abspath(path):
    ret = os.path.abspath(path)
    if path.endswith(os.path.sep):
        ret += os.path.sep
    return ret
