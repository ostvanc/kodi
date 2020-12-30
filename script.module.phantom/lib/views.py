# -*- coding: utf-8 -*-

import re,os, sys
import xbmc,xbmcaddon,xbmcplugin,xbmcgui,xbmcvfs

try:
    from sqlite3 import dbapi2 as database
except:
    from pysqlite2 import dbapi2 as database
addonInfo = xbmcaddon.Addon().getAddonInfo
dataPath = xbmc.translatePath(addonInfo('profile')).decode('utf-8')
databaseFile = os.path.join(dataPath, 'settings.db')
import dialog

def log(msg):
        xbmc.log(msg,level=xbmc.LOGNOTICE)

def addView(content):
    try:
        skin = xbmc.getSkinDir()
        skinPath = xbmc.translatePath('special://skin/')
        xml = os.path.join(skinPath,'addon.xml')
        file = xbmcvfs.File(xml)
        read = file.read().replace('\n','')
        file.close()
        try: src = re.compile('defaultresolution="(.+?)"').findall(read)[0]
        except: src = re.compile('<res.+?folder="(.+?)"').findall(read)[0]
        src = os.path.join(skinPath, src)
        src = os.path.join(src, 'MyVideoNav.xml')
        file = xbmcvfs.File(src)
        read = file.read().replace('\n','')
        file.close()
        views = re.compile('<views>(.+?)</views>').findall(read)[0]
        views = [int(x) for x in views.split(',')]
        for view in views:
            label = xbmc.getInfoLabel('Control.GetLabel(%s)' % (view))
            if not (label == '' or label == None): break
        record = (skin, content, str(view))
        xbmcvfs.mkdir(dataPath)
        dbcon = database.connect(os.path.join(dataPath, 'settings.db'))
        dbcur = dbcon.cursor()
        dbcur.execute('''CREATE TABLE IF NOT EXISTS views (skin TEXT, view_type TEXT, view_id TEXT, UNIQUE(skin, view_type))''')
        dbcur.execute("DELETE FROM views WHERE skin = '%s' AND view_type = '%s'" % (record[0], record[1]))
        dbcur.execute("INSERT INTO views Values (?, ?, ?)", record)
        dbcon.commit()
        viewName = xbmc.getInfoLabel('Container.Viewmode')

        dialog.infoDialog(viewName,'jest teraz widokiem domyślnym')
    except:
        return

def setView(content, viewDict=None):
    try:
        skin = xbmc.getSkinDir()
        dbcon = database.connect(databaseFile)
        dbcur = dbcon.cursor()
        dbcur.execute("SELECT * FROM views WHERE skin = '%s' AND view_type = '%s'" % (skin, content))
        view = dbcur.fetchone()
        view = view[2]
        if view == None: raise Exception()
        return xbmc.executebuiltin('Container.SetViewMode(%s)' % str(view))
    except:
        try: return xbmc.executebuiltin('Container.SetViewMode(%s)' % str(viewDict[skin]))
        except: return
