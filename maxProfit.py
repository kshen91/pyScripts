#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: cylisery@outlook.com

def maxProfit( price ):

    i = 0
    longPrice = 0
    shortPrice = 0
    maxProfit = -1

    while i < (len(price) - 1):
        if maxProfit == -1 or price[i] < longPrice:
            longPrice = price[i]
        shortPrice = price[i+1]

        if (shortPrice - longPrice) > maxProfit:
            maxProfit = shortPrice - longPrice

        i+=1

        print "Loop %d, current maximum profit is %d" % (i,maxProfit)

    return maxProfit

print maxProfit([35,10,50,20,36,88,44,55,21,0,90])
