# coding:utf-8

from math import ceil

def format_str_with_limit(s :str, limit :int, limiter='\n') -> str:

    _s = ''
    i = 0
    for c in s:
        _s += c
        i += 1
        if i == limit:
            i = 0
            _s += limiter
    return _s

def get_str_size_by_limit(s :str, limit :int = 20) -> tuple[int, int]:
    
    """
        RETURN 
            (width, height) of the given string s
    """
    width = (len(s), limit)[len(s)>limit]
    return (width, ceil(len(s) / limit))