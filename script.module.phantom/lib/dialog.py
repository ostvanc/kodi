# -*- coding: utf-8 -*-

import os, xbmc, xbmcgui


def infoDialog(heading, message, icon=None, time=3000):
    xbmcgui.Dialog().notification(heading, message, icon, time, sound=False)

def inputSearchText(text=''):
        textnew = None
        kb = xbmc.Keyboard(text)
        kb.doModal()
        if (kb.isConfirmed()):
            textnew = kb.getText()
        return textnew