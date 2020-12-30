# -*- coding: utf-8 -*-

import os, urllib
import xbmcgui


def cda(videofile):
    a = videofile
    cc =len(a)
    linkvid=''
    for e in range(cc):
        f = ord(a[e])
        if f >=33 or f <=126:
            b=chr(33 + (f + 14) % 94)
        else:
            b=chr(f)
        linkvid+=b
    linkvid = linkvid.replace(".cda.mp4", "")
    linkvid = linkvid.replace(".2cda.pl", ".cda.pl")
    linkvid = linkvid.replace(".3cda.pl", ".cda.pl")
    linkvid = linkvid.replace(".3cda.pl", ".cda.pl")
    linkvid = linkvid[:linkvid.index('0"')]
    if not linkvid.startswith('http'):
        linkvid = 'https://'+linkvid
    if not linkvid.endswith('.mp4'):
        linkvid += '.mp4'
    return linkvid

def drmlistitem(str_url):
    play_item=''
    stream_url=str_url['manifest']
    PROTOCOL = 'mpd'
    DRM = 'com.widevine.alpha'
    LICENSE_URL=str_url['drm_url']
    headr = urllib.quote(str_url['drmheader'])
    import inputstreamhelper
    is_helper = inputstreamhelper.Helper(PROTOCOL, drm=DRM)
    if is_helper.check_inputstream():
        hea = 'Content-Type=&x-dt-custom-data='+headr
        play_item = xbmcgui.ListItem(path=stream_url)
        play_item.setContentLookup(False)
        play_item.setProperty('inputstreamaddon', is_helper.inputstream_addon)
        play_item.setMimeType('application/xml+dash')
        play_item.setProperty('inputstream.adaptive.manifest_type', PROTOCOL)
        play_item.setProperty('inputstream.adaptive.license_type', DRM)
        play_item.setProperty('inputstream.adaptive.license_key', LICENSE_URL+'|' + hea+'|R{SSM}|')
    return play_item