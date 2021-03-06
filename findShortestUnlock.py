#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: cylisery@outlook.com

import time
from collections import deque

def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print '%s function took %0.3f ms' % (f.func_name, (time2-time1)*1000.0)
        return ret
    return wrap

@timing
def FindShortestUnlockPath(target, deadends):
    '''
    target: a four digits number, like "1234"
    deadlocks: a list of four digits number, which can not pass
    '''

    if '0000' in deadends:
        return -1

    path = deque(['0000'])
    visited = set(deadends)
    depth = -1

    parent = {}
    parent['0000'] = None

    while path:
        size = len(path)
        depth += 1
        for _ in xrange(size):
            curState = path.popleft()
            if curState == target:
                # find target & print route for information
                route = deque()
                while curState is not None:
                    route.appendleft(curState)
                    curState = parent[curState]
                print ' '.join(route)

                return depth

            if curState in visited:
                continue
            visited.add(curState)
            nextStates = GetAdjacencies(curState)
            path.extend(nextStates)

            for state in nextStates:
                if state not in visited:
                    parent[state] = curState

    return -1

def GetAdjacencies(state):
    res = []
    for i, ch in enumerate(state):
        num = int(ch)
        res.append(state[:i] + str((num - 1) % 10) + state[i+1:])
        res.append(state[:i] + str((num + 1) % 10) + state[i+1:])
    return res
