#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: kai.shen@mujin.co.jp
# Date: 2019.01.16

import sys, os
import h5py
import ujson

def Main( datafile, path, limitNr ):
    assert os.path.isdir(path)

    dict = {}
    counter = 0
    localDir = path[len('/media/mujin/'):]
    brokenFileList = LoadBrokenFileList(localDir)

    try:
        os.makedirs(localDir)
    except:
        pass

    for root, dirs, files in os.walk(path):
        for filename in files:
            if filename.endswith('.h5') and (not filename.endswith('.png.h5')) and (not filename.endswith('.cloudobstacle.h5')) and (not filename.endswith('.constructor.h5')):
                # get path to h5 file
                fullname = root+'/'+filename
                if (fullname in brokenFileList) or (os.path.islink(fullname)):
                    continue

                print "Loading file: %s" % fullname

                # try read confidences data
                try:
                    f = h5py.File(fullname,'r')

                except: # some file can be failed to open
                    WriteBrokenFileList(localDir, fullname)

                    # increase a counter to indicate that script is not dead
                    counter += 1
                    print "Script is still running, h5 file counter: %d" % counter

                else:
                #with h5py.File(fullname,'r') as f:
                    if 'result' in f:
                        result = ujson.loads(f['result'].value)
                        confidences = [ujson.loads(detectedobject['confidence'])['global_confidence'] for detectedobject in result['detectedobjects']]

                        # add to dictionary
                        dict[fullname] = {'confidences' : confidences, 'minimum' : min(confidences)}

                        # increase a counter to indicate that script is not dead
                        counter += 1
                        print "Script is still running, h5 file counter: %d" % counter

                        if (limitNr) > 0 and (counter >= limitNr):
                            break

        if (limitNr > 0 and counter >= limitNr):
            break

    # saving data to correct place
    with open( localDir+'/'+datafile, 'w') as fp:
        ujson.dump(dict, fp)

def WriteBrokenFileList(localDir, brokenFile):
    fileName = localDir+'/broken_h5_files.json'

    if os.path.isfile(fileName) and (os.stat(fileName).st_size != 0):
        with open(fileName, 'r') as f:
            originList = ujson.load(f)
        f.close()
    else:
        originList = []

    if brokenFile in originList:
        pass
    else:
        originList.append(brokenFile)
        print "Write '%s' to broken file list" % brokenFile
        with open(fileName, 'w') as f:
            ujson.dump(originList, f)

def LoadBrokenFileList(localDir):
    fileName = localDir+'/broken_h5_files.json'

    if os.path.isfile(fileName) and (os.stat(fileName).st_size != 0):
        with open(fileName, 'r') as f:
            list = ujson.load(f)

        return list
    else: # file not exist or empty
        return []

if __name__ == '__main__':
    fileName = sys.argv[1]
    path = sys.argv[2]
    if len(sys.argv) == 4:
        limitNr = int(sys.argv[3])
    else:
        limitNr = -1 # no limit, running for whole dir

    Main(fileName, path, limitNr)
