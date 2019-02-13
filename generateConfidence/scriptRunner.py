#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: cylisery@outlook.com
# Date: 2019.01.17

from multiprocessing import Pool
from generateConfidenceDict import WriteBrokenFileList

import os, sys
import ujson

def runner(path):
    print "Running process %s for dir: %s" % (os.getpid(), path)

    # create a sub folder system
    localDir = path[len('/media/mujin/'):]
    try:
        os.makedirs(localDir)
    except:
        pass # folder exist

    datafile = path.split('/')[-1] + '.json'

    executionString = './generateConfidenceDict.py ' + datafile + ' ' + path
    print "Exec String %s: %s" % (os.getpid(), executionString)

    if os.system(executionString) == 0:
        return
    else:
        errorMsg = os.popen(executionString).readlines()
        brokenFileName = errorMsg[-1][len('Loading file: '):-1]
        WriteBrokenFileList(localDir, brokenFileName)

        # ater written the broken file lise, try run again
        runner(path)



if __name__ == '__main__':
    assert len(sys.argv) == 2, 'Need argument <pathList.json>'
    assert os.path.isfile(sys.argv[1])

    with open(sys.argv[1], 'r') as f:
        pathList = ujson.load(f)

    # create multi-processes for all dirs
    print('Parent process %s.' % os.getpid())

    p = Pool()
    for i in range(len(pathList)):
        p.apply_async(runner, args=(pathList[i],))

    p.close()
    p.join()
    print('All subprocess done!')
    


