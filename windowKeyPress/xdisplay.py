# -*- coding: utf-8 -*-
# Author: cylisery@outlook.com

from copy import copy
from Xlib import X, display
from Xlib import __version__ as XlibVer
from Xlib.ext.record import AllClients
from Xlib.protocol.rq import EventField

from .xwindow import XWindow

from .logconfig import ConfigureLog
log = ConfigureLog(__name__)

if XlibVer < (0, 25):
    log.warning("Xlib version is older than 0.25, suggest to update Xlib to make sure proper behaivor")


class XDisplay(object):

    def __init__(self, disp=None):
        self._display = display.Display(disp)
        self._display2 = display.Display(disp)
        self._root = self._display.screen().root

        self._nrOfWindow = 0
        self._winNameDict = {} # key:(winClass, winName),value:[XWindow]
        self._winIdDict = {}   # key:winId, value:[XWindow]
        self._winList = []

        self._UpdateViewableWindowHierarchy(self._root)

    def _UpdateViewableWindowHierarchy(self, window, bOnlyExecuteActive=True, bPrintWindows=False, winHierarchyList=[]):
        # reset counter and dict if check from root
        if window == self._root:
            self._nrOfWindow = 0
            self._winNameDict = {}
            self._winIdDict = {}
            self._winList = []
        else:
            winHierarchyList = copy(winHierarchyList)
            winHierarchyList.append(window)

        winName = window.get_wm_name()
        winClass = None if window.get_wm_class() is None else window.get_wm_class()[0]
        if winClass is not None and winName is not None:
            self._nrOfWindow += 1
            rootWinOfApp = winHierarchyList[0]
            winObj = XWindow(self._display, rootWinOfApp, window)

            # update idDict
            self._winIdDict[rootWinOfApp.id] = winObj

            # update nameDict
            nameKey = (winClass, winName) # it's possble to have same values for this key
            if nameKey in self._winNameDict.keys():
                self._winNameDict[nameKey].append(winObj)
            else:
                self._winNameDict[nameKey] = [winObj]

            # update winList
            self._winList.append([rootWinOfApp.id, nameKey])

            if bPrintWindows:
                print("%d - winId:[%d], winClass:[%s], winName:[%s], xy=%r, size=%r" % (self._nrOfWindow, rootWinOfApp.id, winClass, winName, winObj.GetXY(), winObj.GetSize()))

            return

        # else try to find name and class in the children
        children = window.query_tree().children
        for w in children:
            if (not bOnlyExecuteActive) or (w.get_attributes().map_state == X.IsViewable):
                geo = w.get_geometry()
                if geo.x >= 0 and geo.y >= 0:
                    self._UpdateViewableWindowHierarchy(w, bOnlyExecuteActive, bPrintWindows, winHierarchyList)

    def ListActiveWindows(self):
        print("Listing all active windows, do not minimize a window if you would like it to be listed here:")
        self._UpdateViewableWindowHierarchy(self._root, True, True)

    def GetWindowList(self):
        return self._winList

    def ListAllWindows(self):
        print("Listing all windows include both actived and inactived ones:")
        self._UpdateViewableWindowHierarchy(self._root, False, True)

    def GetWindowByClassAndName(self, winClass, winName):
        inquiryKey = (winClass, winName)
        if inquiryKey in self._winNameDict.keys():
            if len(self._winNameDict[inquiryKey]) > 1:
                log.warning("More than one window has winClass:<%s> and winName:<%s>, please try to make it unique by minimizing or closing same windows, and try again. \
                           Or try to use GetWindowById() function", winClass, winName)
                return None
            return self._winNameDict[inquiryKey][0]

        log.warning("window with winClass:<%s> and winName:<%s> can not be found", winClass, winName)
        return None

    def GetWindowById(self, winId):
        if winId in self._winIdDict.keys():
            return self._winIdDict[winId]

        log.warning("window with winId:<%s> can not be found", winId)
        return None

    def _WaitClick(self, offset):
        (offsetX, offsetY) = offset
        ctx = self._display.record_create_context(
            0,
            [AllClients],
            [{
                'core_requests': (0, 0),
                'core_replies': (0, 0),
                'ext_requests': (0, 0, 0, 0),
                'ext_replies': (0, 0, 0, 0),
                'delivered_events': (0, 0),
                'device_events': (X.KeyPress, X.MotionNotify),
                'errors': (0, 0),
                'client_started': False,
                'client_died': False,
            }]
        )

        holder = {'X': None, 'Y': None}

        def OnEvent(r, holder):
            data = r.data
            while len(data):
                event, data = EventField(None).parse_binary_value(data, self._display.display, None, None)
                if event.type == X.ButtonPress:
                    holder['X'] = event.root_x - offsetX
                    holder['Y'] = event.root_y - offsetY
                    self._display2.record_disable_context(ctx)
                    self._display2.flush()
        try:
            self._display.record_enable_context(ctx, lambda r: OnEvent(r, holder))
        finally:
            self._display.record_free_context(ctx)
        return holder['X'], holder['Y']

    def GetClickedXY(self, baseWin=None):
        print('Waiting for click')
        offset = (0, 0) if baseWin is None else baseWin.GetXY()
        x, y = self._WaitClick(offset)
        if baseWin is None:
            print('Clicked at (%d,%d)' % (x, y))
        else:
            print('Clicked at (%d,%d) in window:%s' % (x, y, baseWin.GetName()))
        return (x, y)
