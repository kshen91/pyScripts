##!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: cylisery@outlook.com

def CalculateMaxArea(arr):
    maxArea = 0
    indexStack = [-1]

    for i, value in enumerate(arr):
        if len(indexStack) == 1 or value >= arr[indexStack[-1]]:
            indexStack.append(i)

        else:
            while len(indexStack) > 1 and value < arr[indexStack[-1]]:
                topIndex = indexStack.pop()
                maxArea = max(maxArea, arr[topIndex]*(i-indexStack[-1]-1))

            indexStack.append(i)

    while len(indexStack) > 1:
        topIndex = indexStack.pop()
        maxArea = max(maxArea, arr[topIndex]*(len(arr)-indexStack[-1]-1))

    return maxArea
