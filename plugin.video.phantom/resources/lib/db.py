# -*- coding: utf-8 -*-

import re,os, sys, base64
import xbmc,xbmcaddon,xbmcplugin,xbmcgui,xbmcvfs

try:
    from sqlite3 import dbapi2 as database
except:
    from pysqlite2 import dbapi2 as database
addonInfo = xbmcaddon.Addon().getAddonInfo
dataPath = xbmc.translatePath(addonInfo('profile')).decode('utf-8')
databaseFile = os.path.join(dataPath, 'settings.db')
import dialog, PhantomCommon
cm = PhantomCommon.common()

def log(msg):
        xbmc.log(msg,level=xbmc.LOGNOTICE)

def writeData(param,value):
    try:
        record = (param, value)
        xbmcvfs.mkdir(dataPath)
        dbcon = database.connect(os.path.join(dataPath, 'settings.db'))
        dbcur = dbcon.cursor()
        dbcur.execute('''CREATE TABLE IF NOT EXISTS params (param INT, value TEXT, UNIQUE(param))''')
        dbcur.execute("DELETE FROM params WHERE param = %s" % (record[0]))
        dbcur.execute("INSERT INTO params Values (%s, %s)" % record)
        dbcon.commit()
    except:
        return


def readParam(param):
    try:
        dbcon = database.connect(databaseFile)
        dbcur = dbcon.cursor()
        dbcur.execute("SELECT value FROM params WHERE param = %s" % (param))
        view = dbcur.fetchone()
        return view[0]
    except:
        return

def getConfig(conf):
    try:
        query_data = { 'url': 'http://www.phantom-kodi.cba.pl/%s.php' % conf, 'use_post': False, 'return_data': True}
        response = cm.getURLRequestData(query_data)
        match = re.compile('param=(.*?)value=(.*?)</th>', re.DOTALL).findall(response)
        for i in range(len(match)):
            writeData(match[i][0],match[i][1])
    except:
        return

def getQuery(query):
    try:
        query_data = { 'url': 'http://www.phantom-kodi.cba.pl/query003.php', 'use_post': True, 'return_data': True}
        response = cm.getURLRequestData(query_data,{ 'query': query })
        query = re.compile('query:(.+?)<>', flags=re.S).findall(response)
        return query[0]
    except:
        return

def writeViewed(id,info,save_viewed):
    try:
        record = (id, info.replace("'",""))
        xbmcvfs.mkdir(dataPath)
        dbcon = database.connect(os.path.join(dataPath, 'movies.db'))
        dbcur = dbcon.cursor()
        dbcur.execute('''CREATE TABLE IF NOT EXISTS viewed (id_stream TEXT, info TEXT)''')
        dbcur.execute("DELETE FROM viewed WHERE id_stream = '"+id+"'")
        dbcur.execute('''INSERT INTO viewed Values ('%s', '%s')''' % record)
        dbcur.execute('DELETE FROM viewed where`_rowid_` < (SELECT MIN(`_rowid_`) from viewed where `_rowid_` in (SELECT `_rowid_` FROM `viewed` ORDER BY `_rowid_` DESC limit %s))' %save_viewed)
        dbcon.commit()
    except:
        return

def readViewed():
    try:
        dbcon = database.connect(os.path.join(dataPath, 'movies.db'))
        dbcur = dbcon.cursor()
        dbcur.execute("SELECT * FROM viewed ORDER BY `_rowid_` DESC")
        arr = dbcur.fetchall()
        return arr
    except:
        return
