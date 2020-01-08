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
def FindShortestUnlockPath(target, deadlocks):
    '''
    target: a four digits number, like "1234"
    deadlocks: a list of four digits number, which can not pass
    '''

    if '0000' in deadlocks:
        return -1

    path = deque()
    visited = []
    shortestLength = {}
    parent = {}

    path.append('0000')
    shortestLength['0000'] = 0
    parent['0000'] = None

    while len(path) > 0:
        curState = path.popleft()
        if curState == target:
            # find target
            ret = shortestLength[curState]

            # also print route for information
            route = deque()
            while curState is not None:
                route.appendleft(curState)
                curState = parent[curState]
            print ' '.join(route)

            return ret

        nextStates = GetAdjacencies(curState, deadlocks)
        visited.append(curState)
        if len(nextStates) == 0:
            # no more steps can move
            return -1

        for state in nextStates:
            if state not in path and state not in visited:
                path.append(state)
                shortestLength[state] = shortestLength[curState] + 1
                parent[state] = curState

    return -1

def GetAdjacencies(state, deadlocks):
    ret = []
    stateList = list(state)
    for i in range(4):
        plusOneState = ''.join(stateList[:i] + [str((int(stateList[i])+1)%10)] + stateList[i+1:])
        minusOneState = ''.join(stateList[:i] + [str((int(stateList[i])-1)%10)] + stateList[i+1:])
        if plusOneState not in deadlocks:
            ret.append(plusOneState)
        if minusOneState not in deadlocks:
            ret.append(minusOneState)

    return ret
