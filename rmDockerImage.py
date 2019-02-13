#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: cylisery@outlook.com

import sys
import subprocess

from subprocess import CalledProcessError

def Main(imageId):

    cmd = 'docker rmi ' + imageId
    try:
        subprocess.check_output(cmd, shell = True)

    except CalledProcessError: #image has dependent child images
        cmd2 = "docker inspect --format='{{.Id}}' $(docker images --filter since=" + imageId + " -q)"
        try:
            result = subprocess.check_output(cmd2, shell = True)
            subImages = result.split('\n')
        except CalledProcessError:
            print 'get children images failed'
            exit(0)

        for subImage in subImages:
            if subImage != '':
                try:
                    subprocess.check_output('docker rmi '+subImage, shell=True)
                except CalledProcessError:
                    print 'remove child docker image failed'

def checkImageId( imageId ):
    rawOutput = subprocess.check_output('docker images -a', shell = True)
    output = rawOutput.split('\n')

    imageIds = []
    for text in output:
        if len(text.split()) > 2:
            imageIds.append(text.split()[2])

    return imageId in imageIds

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "need image id as input"
        exit(0)
    else:
        imageId = sys.argv[1]
        if checkImageId(imageId):
            Main(sys.argv[1])
        else:
            print "image id not exist"
            exit(0)
