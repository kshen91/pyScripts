# -*- coding: utf-8 -*-
# Author: cylisery@outlook.com

import numpy
import time

from ewmh import EWMH

from Xlib import X
from Xlib import __version__ as XlibVer
from Xlib.XK import string_to_keysym
from Xlib.ext.xtest import fake_input

from PIL.Image import frombytes as ImageFromBytes
from .keymap import key_mapping, NeedShift

from .logconfig import ConfigureLog
log = ConfigureLog(__name__)

if XlibVer < (0, 25):
    log.warning("Xlib version is older than 0.25, suggest to update Xlib to make sure proper behaivor")

class XWindow(object):

    def __init__(self, disp, rootWin, activeWin):
        self._display = disp
        self._rootWin = rootWin     # root window contains coordinate information
        self._activeWin = activeWin # active window contains class and name information, coordinate is relative to rootWin

    def _PrintWindowHierarchy(self, window, indent):
        print("%s winId:%d winClass:%s, winName:%s" % (indent, window.id, window.get_wm_class(), window.get_wm_name()))
        children = window.query_tree().children
        for w in children:
            self._PrintWindowHierarchy(w, indent+'-')

    def PrintWindowHierarchy(self):
        self._PrintWindowHierarchy(self._rootWin, '-')

    def GetXY(self):
        rootGeo = self._rootWin.get_geometry()
        activeGeo = self._activeWin.get_geometry()
        return (rootGeo.x + activeGeo.x, rootGeo.y + activeGeo.y)

    def GetSize(self):
        geo = self._activeWin.get_geometry()
        return (geo.width, geo.height)

    def GetId(self):
        return self._rootWin.id

    def GetName(self):
        return self._activeWin.get_wm_name()

    def GetClass(self):
        return self._activeWin.get_wm_class()[0]

    def Maximize(self):
        ewmh = EWMH(self._display)
        ewmh.setWmState(self._activeWin, 1, "_NET_WM_STATE_MAXIMIZED_VERT")
        ewmh.setWmState(self._activeWin, 1, "_NET_WM_STATE_MAXIMIZED_HORZ")
        ewmh.display.flush()

    def UnMaximize(self):
        ewmh = EWMH(self._display)
        ewmh.setWmState(self._activeWin, 0, "_NET_WM_STATE_MAXIMIZED_VERT")
        ewmh.setWmState(self._activeWin, 0, "_NET_WM_STATE_MAXIMIZED_HORZ")
        ewmh.display.flush()

    def SetFocus(self):
        self._activeWin.configure(stack_mode=X.Above)
        self._activeWin.set_input_focus(X.RevertToParent, X.CurrentTime)
        self._display.sync()
        time.sleep(0.1)

    def Resize(self, w, h):
        self.UnMaximize() # can not resize if maximized
        self._activeWin.configure(width=w, height=h)
        self._display.sync()
        time.sleep(0.1)

    def MoveTo(self, x, y):
        self.UnMaximize()
        self._activeWin.configure(x=x, y=y)
        self._display.sync()
        time.sleep(0.1)

    def GetImageRaw(self, x, y, w, h):
        ''' return: (targetImage, fullImage)
        '''
        width, height = self.GetSize()
        image = self._activeWin.get_image(0, 0, width, height, X.ZPixmap, 0xFFFFFFFF).data
        image = ImageFromBytes('RGB', (width, height), image, 'raw', 'RGBX')
        image = numpy.asarray(image)

        return image[y:(y+h), x:(x+w)], image

    def ClickAt(self, x, y, interval=0.25):
        (offsetX, offsetY) = self.GetXY()
        x, y = x+offsetX, y+offsetY

        self.SetFocus()
        fake_input(self._display, X.MotionNotify, x=x, y=y)
        fake_input(self._display, X.ButtonPress, 1)
        self._display.flush()

        time.sleep(interval)

        fake_input(self._display, X.MotionNotify, x=x, y=y)
        fake_input(self._display, X.ButtonRelease, 1)
        self._display.flush()

    def Drag(self, fromxy, toxy, interval=0.05, step=100):
        (offsetX, offsetY) = self.GetXY()
        fromxy, toxy = list(fromxy), list(toxy)
        fromxy[0] += offsetX
        fromxy[1] += offsetY
        toxy[0] += offsetX
        toxy[1] += offsetY

        fake_input(self._display, X.MotionNotify, x=fromxy[0], y=fromxy[1])
        fake_input(self._display, X.ButtonPress, 1)
        self._display.flush()
        for i in range(step):
            x = int(fromxy[0] + (toxy[0] - fromxy[0]) * (i + 1) / step)
            y = int(fromxy[1] + (toxy[1] - fromxy[1]) * (i + 1) / step)
            fake_input(self._display, X.MotionNotify, x=x, y=y)
            self._display.sync()
            time.sleep(interval)
        fake_input(self._display, X.ButtonRelease, 1)
        self._display.flush()

    def KeyPress(self, keyName, interval=0.25):
        keysym = string_to_keysym(keyName)
        if keysym == 0: # wrong key name is used, try to mapping in the dict
            keysym = string_to_keysym(key_mapping[keyName])
            if keysym == 0:
                log.error("keyName %s can not be found, please check the correct keyname by typing xev in terminal")
                return

        keycode = self._display.keysym_to_keycode(keysym) # 1 and ! will have same keycode

        self.SetFocus()
        if NeedShift(keyName):
            fake_input(self._display, X.KeyPress, 50) # 50 is keycode for Shift_L

        fake_input(self._display, X.KeyPress, keycode)
        time.sleep(interval)
        fake_input(self._display, X.KeyRelease, keycode)

        if NeedShift(keyName):
            fake_input(self._display, X.KeyRelease, 50) # 50 is keycode for Shift_L

        self._display.flush()
