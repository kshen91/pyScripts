#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: cylisery@outlook.com

import sys
import time
import math

def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print '%s function took %0.3f ms' % (f.func_name, (time2-time1)*1000.0)
        return ret
    return wrap

@timing
def modPow(a,n):

    answer = abs(a)

    exp = n

    while n > 1:
        added = 0
        for i in range(0, abs(a)):
            added += answer
        answer = added
        n -= 1

    if a < 0 and exp % 2 == 1:
        return -answer
    else:
        return answer

@timing
def sysPow(a,n):
    return math.pow(int(sys.argv[1]), int (sys.argv[2]))

print modPow(int(sys.argv[1]), int (sys.argv[2]))
print sysPow(int(sys.argv[1]), int (sys.argv[2]))
