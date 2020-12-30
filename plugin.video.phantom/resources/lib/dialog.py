# -*- coding: utf-8 -*-

import os, xbmcgui


def infoDialog(heading, message, icon=None, time=3000):
    xbmcgui.Dialog().notification(heading, message, icon, time, sound=False)