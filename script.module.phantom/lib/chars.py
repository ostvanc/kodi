# -*- coding: utf-8 -*-

import xbmc
import dialog


def log(msg):
        xbmc.log(msg,level=xbmc.LOGNOTICE)

def repPolChars(txt):
        txt = txt.replace('\xc4\x85','a').replace('\xc4\x84','A')
        txt = txt.replace('\xc4\x87','c').replace('\xc4\x86','C')
        txt = txt.replace('\xc4\x99','e').replace('\xc4\x98','E')
        txt = txt.replace('\xc5\x82','l').replace('\xc5\x81','L')
        txt = txt.replace('\xc5\x84','n').replace('\xc5\x83','N')
        txt = txt.replace('\xc3\xb3','o').replace('\xc3\x93','O')
        txt = txt.replace('\xc5\x9b','s').replace('\xc5\x9a','S')
        txt = txt.replace('\xc5\xba','z').replace('\xc5\xb9','Z')
        txt = txt.replace('\xc5\xbc','z').replace('\xc5\xbb','Z')
        return txt


