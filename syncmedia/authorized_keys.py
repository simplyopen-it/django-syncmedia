# -*- coding: utf-8 -*-
import os

def get_keys(file_path):
    try:
        with open(file_path, 'r') as fd:
            ret = fd.readlines()
    except IOError:
        ret = []
    return [line.rstrip(os.linesep) for line in ret]

def is_in(key, file_path):
    keys = get_keys(file_path)
    return key in keys

def add_key(key, file_path):
    if not is_in(key, file_path):
        with open(file_path, 'a') as fd:
            fd.write(key + os.linesep)

def add_keys(keys, file_path):
    authorized_keys = set(get_keys(file_path))
    keys = set(keys)
    not_auth = keys - authorized_keys
    with open(file_path, 'a') as fd:
        fd.writelines([key + os.linesep for key in not_auth])

def del_key(key, file_path):
    keys = get_keys(file_path)
    keys.remove(key)
    with open(file_path, 'w') as fd:
        fd.writelines([key + os.linesep for key in keys])

def del_keys(keys, file_path):
    authorized_keys = set(get_keys(file_path))
    keys = set(keys)
    to_write = authorized_keys - keys
    with open(file_path, 'w') as fd:
        fd.writelines([key + os.linesep for key in to_write])
