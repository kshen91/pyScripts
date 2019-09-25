# -*- coding: utf-8 -*-
# Author: cylisery@outlook.com

import os
import cv2
import json
import numpy
import time

from .xdisplay import XDisplay
from .logconfig import ConfigureLog
log = ConfigureLog(__name__)

def NeedWindow(func):
    def wrapper(self, *args, **kwargs):
        if self._window is not None:
            return func(self, *args, **kwargs)
        log.warning("Need to set window for gui first to call this function!")
        return None
    return wrapper

class GUI(object):

    def __init__(self, display, dataDir, winClass='', winName='', winId=None):
        self._dataDir = dataDir

        self._display = XDisplay(display)
        if winId is not None:
            self._window = self._display.GetWindowById(winId)
        else:
            self._window = self._display.GetWindowByClassAndName(winClass, winName) # can return None

    def ListActiveWindows(self):
        '''Note:this function will update listed windows into window_list in XDisplay
        '''
        self._display.ListActiveWindows()

    def ListAllWindows(self):
        '''Note:this function will update listed windows into window_list in XDisplay
        '''
        self._display.ListAllWindows()

    def GetWindowInfoList(self):
        return self._display.GetWindowList()

    def SetWindowByClassAndName(self, winClass, winName):
        newWin = self._display.GetWindowByClassAndName(winClass, winName)
        if newWin is not None:
            self._window = newWin

    def SetWindowById(self, winId):
        newWin = self._display.GetWindowById(winId)
        if newWin is not None:
            self._window = newWin

    def DisconnectWindow(self):
        self._window = None

    def GetCurrentWindow(self):
        if self._window is None:
            return None

        return self._window

    @NeedWindow
    def WaitImageRecord(self, name, xy1=None, xy2=None):
        log.info('Record Image: name = %s', name)
        if xy1 is None or xy2 is None:
            x1, y1 = self.GetClickedXY()
            x2, y2 = self.GetClickedXY()
        else:
            x1, y1 = xy1
            x2, y2 = xy2

        x = min(x1, x2)
        y = min(y1, y2)
        w = abs(x1 - x2)
        h = abs(y1 - y2)
        baseW, baseH = self._window.GetSize()

        with open(self._dataDir + '/' + name + '.json', 'w') as f:
            json.dump({'x': x, 'y': y, 'w': w, 'h': h, 'baseW': baseW, 'baseH': baseH}, f)

        image = self._window.GetImageRaw(x, y, w, h)[0]
        cv2.imwrite(self._dataDir + '/' + name + '.png', image)

        cv2.imshow('image', image)
        cv2.waitKey(100) # msec
        return True

    @NeedWindow
    def GetClickedXY(self):
        return self._display.GetClickedXY(self._window)

    @NeedWindow
    def Click(self, name):
        x, y = self._GetDataForResource(name, 'GetClickPoint')
        baseSize = self._GetDataForResource(name, 'GetBaseSize')
        if baseSize is not None:
            # resize the window to the size when doing record
            self._window.Resize(baseSize[0], baseSize[1])

        self._window.ClickAt(x, y)

    @NeedWindow
    def KeyPress(self, keyName):
        self._window.KeyPress(keyName)

    @NeedWindow
    def InputString(self, string):
        for ch in string:
            self.KeyPress(ch)

    @NeedWindow
    def Drag(self, nameFrom, nameTo):
        fromxy = self._GetDataForResource(nameFrom, 'GetClickPoint')
        toxy = self._GetDataForResource(nameTo, 'GetClickPoint')
        self._window.Drag(fromxy, toxy)

    @NeedWindow
    def WaitImage(self, name, threshold=10.0, maxerrorrate=0.1, interval=0.2, timeout=5.0):
        imRecord = cv2.imread(self._dataDir + '/' + name + '.png')
        x, y, w, h = self._GetDataForResource(name, 'GetXYWH')

        starttime = time.time()
        while True:
            imCurrent, imFull = self._window.GetImageRaw(x, y, w, h)
            cv2.imshow('image', imCurrent)
            cv2.imshow('image', numpy.vstack([imRecord, imCurrent, imCurrent - imRecord]))
            cv2.waitKey(100) # msec

            # calculate pixel errors. if any channel value in a pixel has larger difference than threshold, treat as a pixel error
            errorpixels = numpy.sum(numpy.any(numpy.abs(imCurrent - imRecord) > threshold, axis=2))
            errorrate = float(errorpixels)/float(w*h)

            if errorrate < maxerrorrate:
                print('found image. errorrate = %f' % errorrate)
                return True
            if timeout and time.time() - starttime > timeout:
                print('failed to image. errorrate = %f' % errorrate)
                return False
            time.sleep(interval)

    def _GetDataForResource(self, name, action):
        filename = self._dataDir + '/' + name + '.json'
        assert os.path.isfile(filename), "Resource json for %s is not exist" % name

        with open(filename, 'r') as f:
            metadata = json.load(f)

        if action == 'GetClickPoint':
            x = int(metadata['x'] + metadata['w'] * 0.5)
            y = int(metadata['y'] + metadata['h'] * 0.5)
            return (x, y)

        if action == 'GetBaseSize':
            if 'baseW' in metadata and 'baseH' in metadata:
                return (metadata['baseW'], metadata['baseH'])
            log.warn('baseW and baseH info is not exist in resource file, might be old resource')
            return None

        if action == 'GetXYWH':
            return (metadata['x'], metadata['y'], metadata['w'], metadata['h'])

        log.error("action: %s is not supported.", action)
        return None
