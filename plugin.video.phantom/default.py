# -*- coding: utf-8 -*-
# imports
import re, os, time, sys, zlib, base64
import urllib, urllib2, urlparse
import xbmcplugin, xbmcgui, xbmcaddon
import string, json
import cookielib
import decoder
import requests

try:
   import StorageServer
except:
   import storageserverdummy as StorageServer
cache = StorageServer.StorageServer("Phantom")

from resources.lib import db,views, tools, dialog
from resources.lib import PhantomCommon, common, metadata

#globals

cm                      = PhantomCommon.common()
cnt                     = common.count()
sysaddon                = sys.argv[0]
addon_handle            = int(sys.argv[1])
args                    = urlparse.parse_qs(sys.argv[2][1:])
my_addon                = xbmcaddon.Addon()
my_addon_id             = my_addon.getAddonInfo('id')
my_addon_name           = my_addon.getAddonInfo('name')

up_info             = my_addon.getSetting('up_info')
cda_login           = my_addon.getSetting('cda_login')
cda_user            = my_addon.getSetting('cda_user')
cda_pass            = my_addon.getSetting('cda_pass')
set_list_colours    = my_addon.getSetting('set_list_colours')
show_adult          = my_addon.getSetting('show_adult')
show_premium        = my_addon.getSetting('show_premium')

SERVICE     = 'cda'
COOKIEPATH  = unicode(my_addon.getAddonInfo('path') + os.path.sep + "cookies",'utf-8')
COOKIEFILE  = COOKIEPATH + os.path.sep + SERVICE + ".cookie"

s = requests.Session()

loginData   = { 'username': cda_user, 'password': cda_pass }
mainUrl     = 'https://www.cda.pl'



def log(msg):
        xbmc.log(msg,level=xbmc.LOGNOTICE)

colours = ('','red','green','blue','yellow')
userSortName = ['alfabetycznie','najnowsze']
userSort = {0:'sortby=name&order=asc',1:'sortby=created&order=desc'}

# Functions
def ownFolders():
        for i in range (1,6):
            Fx = "F"+str(i)
            if my_addon.getSetting(Fx)=="true":
                add(my_addon.getSetting(Fx+"_nazwa"),seturl(Fx),'FilmList',True)

def categories():
        menuTable = {
            1: ["[COLOR=%s]Phantom Extra[/COLOR]" % ('blue' if set_list_colours == 'true' else ''),"0","PhantomExtra"],
            2: ["[COLOR=%s]Filmy - HD[/COLOR]" % ('red' if set_list_colours == 'true' else ''),db.readParam(11) +'duration=dlugie&quality=720p&s=date',"FilmList"],
            3: ["[COLOR=%s]Filmy - najnowsze[/COLOR]" % ('green' if set_list_colours == 'true' else ''),db.readParam(11) +'duration=dlugie&s=date',"FilmList"],
            4: ["Filmy - PREMIUM",mainUrl+ '/premium',"PremiumCategory"],
            5: ["Filmy - najpopularniejsze",db.readParam(11) +'s=popular',"FilmList"],
            6: ["Filmy - najlepiej oceniane",db.readParam(11) +'s=rate',"FilmList"],
            7: ["Filmy - najtrafniejsze",db.readParam(11) +'s=best',"FilmList"],
            8: ["Filmy - alfabetycznie",db.readParam(11) +'s=alf',"FilmList"],
            9: ["[COLOR=%s]Video - najnowsze[/COLOR]" % ('green' if set_list_colours == 'true' else ''),mainUrl+ '/video',"VideoList"],
            10: ["Video - najlepiej oceniane",mainUrl+ '/video?o=top&k=miesiac',"VideoList"],
            11: ["Video - ekstremalne",mainUrl+ '/video/kat24',"VideoList"],
            12: ["Video - krótkie filmy i animacje",mainUrl+ '/video/kat26',"VideoList"],
            13: ["Video - motoryzacja, wypadki",mainUrl+ '/video/kat27',"VideoList"],
            14: ["Video - muzyka",mainUrl+ '/video/kat28',"VideoList"],
            15: ["Video - prosto z Polski",mainUrl+ '/video/kat29',"VideoList"],
            16: ["Video - rozrywka",mainUrl+ '/video/kat30',"VideoList"],
            17: ["Video - sport",mainUrl+ '/video/kat31',"VideoList"],
            18: ["Video - śmieszne filmy",mainUrl+ '/video/kat32',"VideoList"],
            19: ["Video - różności",mainUrl+ '/video/kat33',"VideoList"],
            20: ["Video - życie studenckie",mainUrl+ '/video/kat34',"VideoList"],
            21: ["[COLOR=%s]Poczekalnia[/COLOR]" % ('yellow' if set_list_colours == 'true' else ''),mainUrl+ '/video/najnowsze',"WaitList"],
            22: ["Narzędzia","0","Tools"],}
        if my_addon.getSetting('save_viewed') <> '0':
            add('Historia oglądania','0','ViewedList',True)
        for i in range(1,23):
            Mx = "M"+str(i)
            if my_addon.getSetting(Mx)=="true":
                add(menuTable[i][0],menuTable[i][1],menuTable[i][2],True)
        add('Ustawienia','0','Settings',True)
        add('[COLOR=%s]Szukaj[/COLOR]' % ('green' if set_list_colours == 'true' else ''),'0','Search',True)

def phantomExtra():
        phantom_user    = my_addon.getSetting('phantom_user')
        phantom_pass    = my_addon.getSetting('phantom_pass')
        try:
            if int(db.readParam(7)):
                exec(db.getQuery(7.004))
                match=re.compile('pozycja</td><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td></tr>', re.DOTALL).findall(response)
                if len(match) > 0:
                    for i in range(len(match)):
                        add(match[i][0],match[i][1],match[i][2],True)
        except:
            pass
        xbmcplugin.endOfDirectory(addon_handle)

def toolsMenu():
        add('Usuń pliki tymczasowe','0','ClearCache',True)
        add('Wyczyść archiwum pobranych wtyczek','0','DeletePackages',True)

        xbmcplugin.endOfDirectory(addon_handle)

def userAccount():
        add('Moje filmy', mainUrl+'/'+cda_user+'/folder-glowny?type=pliki&', 'UserFilm', True, user=cda_user)
        add('Ulubione filmy', mainUrl+'/'+cda_user+'/ulubione/folder-glowny?type=pliki&','UserFilm',True, user=cda_user)
        xbmcplugin.endOfDirectory(addon_handle)

def userFilm(url,folderName):
        xbmcplugin.setContent(addon_handle, 'movies')
        owner = args.get('owner', [''])[0]
        try:
            log_par = int(db.readParam(5))
        except:
            pass
        sort_id = int(my_addon.getSetting('user_film_sort')) if my_addon.getSetting('user_film_sort') else 1
        sort_name = userSortName[sort_id]
        sort = userSort.get(sort_id)
        url = url + sort
        if cdaLogin():
            query_data = { 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE,'use_post': False, 'return_data': True}
            link = cm.getURLRequestData(query_data)
        else:
            link = getLink(url)
        if link.startswith('Error'):
             return

        strona = 1
        active = re.search('active "><a>(.*?)<',link)
        if active:
            strona = int(active.group(1))
        nextPage = re.compile('Następna strona(.*?)active(.*?)href="(.*?)"', re.DOTALL).findall(link)
        if strona == 1:
            if folderName == '[COLOR=orange][..] (Przejdź wyżej)[/COLOR]':
                folderName = re.search('name-folder-big-ico">(.*?)<', link)
                folderName = folderName.group(1)
            add(common.htmlSpecialChars(folderName + ' [COLOR=red]'+sort_name +'[/COLOR] [zmień]'), str(abs(sort_id-1)),'UserFilmSort', True)

            labels = re.compile('folder-area"> <a(.*?)span></a', re.DOTALL).findall(link)
            for label in labels:
                folder_url = re.compile('href="(.*?)"').findall(label)
                folder_name = re.compile('name-folder">(.*?)<').findall(label)

                folder_url = folder_url[0] + '?type=pliki&'
                folder_name = folder_name[0]

                contextm = []
                contextm.append(('Ustaw bieżący widok jako domyślny', 'RunPlugin(%s?mode=addView&content=user)' % sysaddon))
                add(common.htmlSpecialChars('[COLOR=orange]'+folder_name+ '[/COLOR]'), folder_url,'UserFilm', True,contextm, user=owner)

        labels2=re.compile('list-when-small tip(.*?)</p>', re.DOTALL).findall(link)
        items = findItems2(labels2,content='Film')
        if items:
            if up_info=='true' and int(db.readParam(4)): items = metadata.getMeta(items)
            for item in items:
                item['owner'] = owner
                watchlvl = 0
                item['content'] = 'Film'
                item['urlref'] = sys.argv[2]
                addItem('DecodeLink',contextmenu(item['url'],item['title_cln'],'UserFilm'),content = 'Film', item = item)
                if item['priv'] == 1 and log_par:
                    try:
                        info = item
                        exec (db.getQuery(8.008))
                    except:
                        pass

        if len(nextPage) > 0:
            add('[COLOR=%s]> Następna strona >[/COLOR]' % ('blue' if set_list_colours == 'true' else ''), nextPage[0][2],'UserFilm', True)
        sort_methods()
        xbmcplugin.endOfDirectory(addon_handle)
        views.setView('UserFilm', {'skin.confluence': 50})

def streamList(url,list_type):
        xbmcplugin.setContent(addon_handle, 'movies')
        response = getLink(url)
        if list_type == 'FilmList':
            labels = re.compile('<label(.*?)</label>', re.DOTALL).findall(response)
            content = 'Film'
        elif list_type == 'VideoList':
            labels = re.compile('<label(.*?)</label>', re.DOTALL).findall(response)
            content = 'Video'
        elif list_type == 'WaitList':
            labels=re.compile('poczekalnia_usu(.*?)</a>\n</div>', re.DOTALL).findall(response)
            content = 'Poczekalnia'

        prevPage = re.compile('onclick="changePage\((.*?)\)(.*?)href="(.*?)"', re.DOTALL).findall(response)
        if len(prevPage) > 0:
            add('[COLOR=%s]< Poprzednia strona (%s) < [/COLOR]' % ('blue' if set_list_colours == 'true' else '', prevPage[0][0]), mainUrl + prevPage[0][2],'ChangePage', False, values=list_type)
        items = findItems(labels,content)
        if items:
            if up_info == 'true' and list_type != 'VideoList' and int(db.readParam(4)):
                items = metadata.getMeta(items)
            for item in items:
                item['urlref'] = sys.argv[2]
                addItem('DecodeLink',contextmenu(item['url'],item['title_cln'],list_type),content, item = item)
        nextPage = re.compile('"javascript:changePage\((.*?)\)(.*?)href="(.*?)"', re.DOTALL).findall(response)
        if len(nextPage) > 0:
            add('[COLOR=%s]> Następna strona (%s) > [/COLOR]' % ('blue' if set_list_colours == 'true' else '', nextPage[0][0]), mainUrl + nextPage[0][2],'ChangePage', False, values=list_type)
        sort_methods()
        xbmcplugin.endOfDirectory(addon_handle)


        views.setView(list_type, {'skin.confluence': 50})
        xbmc.executebuiltin('Control.SetFocus('+str(addon_handle)+',12)')


def extraList(url,list_type):
        xbmcplugin.setContent(addon_handle, 'movies')
        query_data = { 'url': url, 'use_post': False, 'return_data': True}
        response = cm.getURLRequestData(query_data)
        response = response.replace('\r\n','').replace('\t','').replace('\n','').replace('\r','')
        streams = re.search('meta_start(.*?)meta_end', response).group(1)
        items = json.loads(streams)
        for item in items:
            item['dursec'] = cnt.durSec(item['duration'])
            if  not item['premium'] == 'P' or show_premium == "true":
                item['urlref'] = sys.argv[2]
                addItem('DecodeLink',contextmenu(item['url'],item['title_cln'],list_type),content=item['content'], item = item)
        sort_methods()
        xbmcplugin.endOfDirectory(addon_handle)
        xbmc.sleep( 1000 )
        views.setView(list_type, {'skin.confluence': 50})

def viewedList(list_type):
        xbmcplugin.setContent(addon_handle, 'movies')
        streams = db.readViewed()
        for stream in streams:
            item = json.loads(stream[1])
            contextmenu = []
            contextmenu.append(('Informacja', 'XBMC.Action(Info)'),)
            contextmenu.append(('[COLOR=gold]Inne filmy autora[/COLOR]', "XBMC.Container.Update(%s+?url=%s&mode=FindAuthor,True)" % (sysaddon,item['url'])),)
            contextmenu.append(('[COLOR=gold]Katalog źródłowy filmu[/COLOR]', "XBMC.Container.Update(%s+?url=%s&mode=FindSource)" % (sysaddon,item['url'])),)
            contextmenu.append(('Wyszukaj podobne', "XBMC.Container.Update(%s+?url=%s&mode=SearchFromList)" % (sysaddon,item['title_cln'])),)
            contextmenu.append(('Ustaw bieżący widok jako domyślny', 'RunPlugin(%s?mode=addView&content=%s)' % (sysaddon,list_type)))
            addItem('DecodeLink',contextmenu,content=item['content'], item = item)
        sort_methods()
        xbmcplugin.endOfDirectory(addon_handle)
        xbmc.sleep( 1000 )
        views.setView(list_type, {'skin.confluence': 50})

def premiumCategory(url):
        prem_sortN = my_addon.getSetting('prem_sortN')
        if not prem_sortN:
            premSort()
            prem_sortN = my_addon.getSetting('prem_sortN')
        add('[COLOR=red]Ostatnio dodane[/COLOR]',url+'?sort=new','PremiumList', True)
        add('Sortuj po: [B]'+prem_sortN+'[/B]',url,'PremiumSort', False)
        link = getLink(url)
        match = re.compile('Filmy i seriale premium(.*?)clear', re.DOTALL).findall(link)
        if len(match) > 0:
            match1 = re.compile('a href="(.*?)">(.*?)<', re.DOTALL).findall(match[0])
            if len(match1) > 0:
                for i in range(len(match1)):
                    add(match1[i][1], match1[i][0].replace('" id="remove_category',''),'PremiumList', True)
        xbmcplugin.endOfDirectory(addon_handle)

def premiumList(url):
        xbmcplugin.setContent(addon_handle, 'movies')
        payload = args.get('values', [''])[0]
        prem_sortV = my_addon.getSetting('prem_sortV')
        if url.find('?sort=')<0:
            url = url + '?sort=' + prem_sortV
        headers= {'user-agent': db.readParam(9)}
        if payload:
            payload = json.loads(payload)
            r = s.post(url,headers=headers,json=payload)
            resp=r.json()
            result = resp['result']
            content = result['html'].encode('utf-8')
        else:
            r = s.post(url,headers=headers)
            content = r.content
        labels=re.compile('cover-area"(.*?)ico-above-24', re.DOTALL).findall(content)
        item = {}
        for label in labels:
            url_film = re.search('href="(.*?)\?', label)
            item['url'] = url_film.group(1)
            item['id_stream'] = item['url'].replace('https://www.cda.pl/video/','')
            title = re.compile('title="(.*?)"', re.DOTALL).findall(label)[0]
            item['title_drt'] = common.htmlSpecialChars(title)
            item['title_stream'] = item['title_drt'].split('(')[0]
            item['title_cln'],item['year'],item['version'] = cleanTitle(item['title_drt'])
            desc = re.compile('description-cover-container">(.*?)<br /><br />(.*?)<span', re.DOTALL).findall(label)
            item['genres'] = desc[0][0]
            item['plot'] = common.htmlSpecialChars(desc[0][1])
            icon = 'https:' + re.search('src="(.*?)"', label).group(1)
            item['icon'] = icon.replace('226x316','299x446')
            rating = re.search('marker">(.*?)<',label)
            item['rating'] = rating.group(1) if rating else ''
            isFolder = 1 if re.search('folder', item['url']) else 0
            tags = re.compile('cloud-gray">(.*?)<', re.DOTALL).findall(label)
            item['res_org'] = tags[0]
            item['premium'] = 'P' if tags[1] == 'Premium' else ''
            item['duration'] = ''
            item['dursec'] = 0
            item['priv'] = 0
            item['savelvl'] = 0
            item['content'] = 'Film'

            if isFolder:
                add(prefiks(item['premium']) + common.htmlSpecialChars('[COLOR=orange]'+item['title_stream'] + '[/COLOR]'), item['url']+'?','UserFilm', True, icon=item['icon'])
            else:
                item['urlref'] = sys.argv[2]
                addItem('DecodeLink',contextmenu(item['url'],item['title_cln'],'PremiumFilm'),content = 'Film', item = item)
        nextpage = re.search('katalogLoadMore\(page,"(.*?)","(.*?)"', content)
        if nextpage:
            page = 1
            payload = {'jsonrpc':'2.0','method':'katalogLoadMore','params':[page+1,nextpage.group(1),nextpage.group(2)],'id':page}
        else:
            payload['id'] += 1
            payload['params'][0] += 1
            page = payload['id']
        add('[COLOR=%s]> Następna strona (%s) > [/COLOR]' % ('blue' if set_list_colours == 'true' else '', page+1), url,'PremiumList', True, values=json.dumps(payload))

        sort_methods()
        xbmcplugin.endOfDirectory(addon_handle)
        views.setView('PremiumFilm', {'skin.confluence': 50})

def findAuthor(url):
        if cdaLogin():
            query_data = { 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE,'use_post': False, 'return_data': True}
            link = cm.getURLRequestData(query_data)
        else:
            link = getLink(url)

        author_search = re.compile('Dodał:(.*?)href="(.*?)"', re.DOTALL).search(link)
        if author_search:
            author = author_search.group(2).replace('/','')
            if not author == '#0':
                author_link = mainUrl + '/' + author
                userFilm(author_link+'/folder-glowny?type=pliki&', author)
            else:
                d = xbmcgui.Dialog()
                d.ok('Info', 'Autor anonimowy. Nie posiada konta')
        else:
            d = xbmcgui.Dialog()
            d.ok('Brak informacji', 'Autor anonimowy')

def findSource(url):
        if cdaLogin():
            query_data = { 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE,'use_post': False, 'return_data': True}
            link = cm.getURLRequestData(query_data)
        else:
            link = getLink(url)

        catalog = re.compile('W katalogu:(.*?)href="(.*?)">(.*?)<', re.DOTALL).search(link)
        if catalog:
            catalog_link = mainUrl + '/' + catalog.group(2)
            catalog_name = catalog.group(3)
            userFilm(catalog_link+'?type=pliki&', catalog_name)
        else:
            findAuthor(url)

def findItems(labels,content):
        items = []
        priv = 0
        for label in labels:
            videoid = re.compile('href=".*?/video/(.*?)".*?>(.*?)<', re.DOTALL).findall(label)
            if videoid:
                id_stream = videoid[0][0]
                title = re.compile('alt="(.*?)"').findall(label)
                if not title:
                    title = (videoid[0][1],)
                plot = re.compile('title="(.*?)"').findall(label)
                duration = re.search('timeElem.+?>(.*?)<', label)
                res = re.search('hd-elem-pos">(.*?)<', label)
                icon = re.compile('src="(.*?)"').findall(label)
                title_drt = common.htmlSpecialChars(title[0])
                title_cln,year,version = cleanTitle(title_drt)
                title_stream = title_drt
                plot = common.htmlSpecialChars(plot[0]) if plot else ''
                url = 'https://www.cda.pl/video/'+id_stream
                duration = duration.group(1) if duration else ''
                dursec = cnt.durSec(duration)
                res_org = res.group(1) if res else ''
                premium = 'P' if label.find('>premium')>0 else ''
                savelvl = 0
                owner = ''
                if  not premium == 'P' or show_premium == "true":
                    if not re.search('adult', str(icon)) or show_adult == "true":
                        icon = 'http:'+icon[0] if icon else ''
                        items.append({'id_stream':id_stream, 'title_cln':unicode(title_cln,'utf-8'), 'title_drt':unicode(title_drt,'utf-8'), 'title_stream':unicode(title_stream,'utf-8'), 'title_org': '', 'plot': unicode(plot,'utf-8'), 'url':url, 'duration': duration, 'dursec':dursec, 'res_org': res_org, 'icon':icon, 'content':content, 'premium':premium, 'year':year, 'version': version, 'priv': priv, 'owner':owner, 'savelvl':savelvl})
        return items


def findItems2(labels,content):
        items = []
        for label in labels:
            t1 = re.compile('href=".*/video\/(.*?)">(.*?)<').findall(label)
            plot = re.compile('alt="(.*?)"', re.DOTALL).findall(label)
            duration = re.compile('time-thumb-fold">(.*?)<').findall(label)
            res = re.compile('hd-ico-elem">(\d*p)<').findall(label)
            icon = re.compile('src="(.*?)"').findall(label)
            premium = 'P' if label.find('premium')>0 else ''
            priv = 1 if label.find('PRYWATNY')>0 else 0
            id_stream = t1[1][0]
            title_drt = common.htmlSpecialChars(t1[1][1])
            title_cln,year,version = cleanTitle(title_drt)
            title_stream = title_drt
            url = mainUrl+'/video/'+id_stream
            plot = common.htmlSpecialChars(plot[0]) if plot else ''
            duration = duration[0]
            dursec = cnt.durSec(duration)
            res_org = res[0] if res else ''
            icon = 'http:'+icon[0] if icon else ''
            savelvl = 0
            owner = ''

            if  not premium == 'P' or show_premium == "true":
                items.append({'id_stream':id_stream, 'title_cln':unicode(title_cln,'utf-8'), 'title_drt':unicode(title_drt,'utf-8'), 'title_stream':unicode(title_stream,'utf-8'), 'title_org': '', 'plot':unicode(plot,'utf-8'), 'url':url, 'duration': duration, 'dursec': dursec, 'res_org': res_org, 'icon':icon, 'content':content, 'premium':premium, 'year':year, 'version': version, 'priv':priv, 'owner':owner, 'savelvl':savelvl})
        return items

def prefiks(premium ='',priv = 0):
    prefiks = ''
    if premium:
        prefiks = '[COLOR=%s][%s] [/COLOR]' % ('red' if set_list_colours == 'true' else '', premium)
    if priv == 1:
        prefiks = prefiks + '[COLOR=%s][R] [/COLOR]' % ('blue' if set_list_colours == 'true' else '')
    return prefiks

def resmask(res):
    if len(res)<4:
        res = '    ---    '
    elif len(res)==4:
        res = '  '+res
    return res


def contextmenu(url,title_cln,list_type):
        title_cln=title_cln.replace('|','l')
        contextmenu = []
        contextmenu.append(('Informacja', 'XBMC.Action(Info)'),)
        contextmenu.append(('[COLOR=gold]Inne filmy autora[/COLOR]', "XBMC.Container.Update(%s+?url=%s&mode=FindAuthor,True)" % (sysaddon,url)),)
        contextmenu.append(('[COLOR=gold]Katalog źródłowy filmu[/COLOR]', "XBMC.Container.Update(%s+?url=%s&mode=FindSource)" % (sysaddon,url)),)
        if up_info=='true':
            contextmenu.append(('Skojarz z Filmweb', "XBMC.Container.Update(%s+?url=%s&mode=SearchMeta)" % (sysaddon,title_cln)),)
            contextmenu.append(('Skojarz z TMDb', "XBMC.Container.Update(%s+?url=%s&mode=SearchMetaTmdb)" % (sysaddon,title_cln)),)
        contextmenu.append(('Wyszukaj podobne', "XBMC.Container.Update(%s+?url=%s&mode=SearchFromList)" % (sysaddon,title_cln)),)
        contextmenu.append(('Ustaw bieżący widok jako domyślny', 'RunPlugin(%s?mode=addView&content=%s)' % (sysaddon,list_type)))
        return contextmenu

def sort_methods():
    xbmcplugin.addSortMethod(addon_handle , sortMethod=xbmcplugin.SORT_METHOD_UNSORTED, label2Mask = '%U ' + '[[COLOR %s]%s [/COLOR]]' % ('green' if set_list_colours == 'true' else ''  ,'%Y') + '%P' )
    xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE, label2Mask = '%U ' + '[[COLOR %s]%s [/COLOR]]' % ('green' if set_list_colours == 'true' else ''  ,'%Y') + '%P' )
    xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RATING)
    xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_VIDEO_YEAR)
    xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_STUDIO)
    xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RUNTIME)
    xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)

def premSort():
    headers= {'user-agent': db.readParam(9)}
    r = s.get(url,headers=headers)
    content = r.content
    sorts = re.compile('data-value="(.*?)"><a>(.*?)<', re.DOTALL).findall(content)
    prem_sortN = []
    prem_sortV = []
    for sort in sorts:
        prem_sortV.append(sort[0])
        prem_sortN.append(sort[1])
    s1 = xbmcgui.Dialog().select('Wybierz sortowanie',prem_sortN)
    if s1 > -1:
        my_addon.setSetting('prem_sortN',prem_sortN[s1])
        my_addon.setSetting('prem_sortV',prem_sortV[s1])
        xbmc.executebuiltin('XBMC.Container.Refresh')


def seturl(Fx):
        fraza = my_addon.getSetting(Fx+"_fraza")
        ldlugosc = ["all","krotkie","srednie","dlugie"]
        iddlugosc = my_addon.getSetting(Fx+"_dlugosc")
        dlugosc = ldlugosc[int(iddlugosc)]
        ljakosc = ["all","480p","720p","1080p"]
        idjakosc = my_addon.getSetting(Fx+"_jakosc")
        jakosc = ljakosc[int(idjakosc)]
        lsort = ["best","date","popular","rate","alf"]
        idsort = my_addon.getSetting(Fx+"_sort")
        sort = lsort[int(idsort)]
        if fraza == '*':
            url = db.readParam(11)+'duration='+dlugosc+'&quality='+jakosc+'&s='+sort
        else:
            fraza = repPolChars(fraza.replace(' ','_'))
            url = mainUrl+ '/video/show/'+fraza+'?duration='+dlugosc+'&quality='+jakosc+'&s='+sort
        return url


def cleanTitle(title):
    pattern = re.compile(r"[(\[{;/-]")
    year=''
    version=''
    reyear = re.search('\d{4}',title)
    reversion = re.compile('(?:lektor|dubbing|napisy)', flags=re.I | re.X).findall(title.lower())
    if reversion:
        version = ' '.join(reversion)
    if reyear:
        yearstr = reyear.group()
        if int(yearstr) > 1900:
            title = re.sub(yearstr,'',title)
            year = yearstr
    title = pattern.split(title)[0]
    title=title.lower()
    rmList=['lektor','dubbing','napisy','cały','film','polski','full','hd','*','720p','1080p','720','1080','"',',','ready','.',' pl']
    for rm in rmList:
        title = title.replace(rm,'')
    return title.strip(), year, version.strip()

def add(name,url,mode,folder,contextmenu='',info='',icon='',content='',premium='',isPlayable = False, user='',values=''):
        u=sysaddon+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&icon="+urllib.quote_plus(icon)+"&content="+content+"&premium="+premium+"&owner="+user+"&values="+values
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=icon)
        if isPlayable:
            liz.setProperty('IsPlayable', 'True')
        if contextmenu:
            liz.addContextMenuItems(contextmenu)
        ok=xbmcplugin.addDirectoryItem(handle=addon_handle,url=u,listitem=liz,isFolder=folder)
        return ok

def addItem(mode='',contextmenu='', info='', content='', item=[]):
        u=sysaddon+"?url="+urllib.quote_plus(item['url'])+"&mode="+str(mode)
        name = prefiks(item['premium'],item.get('priv')) + item['title_stream'] + ' - ' + '[COLOR=%s]%s[/COLOR]' % ( 'green' if set_list_colours == 'true' else '', item['duration'] )
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png")
        info = { 'title':name, 'sorttitle':item['title_stream'], 'code': '[COLOR %s]%s[/COLOR][COLOR %s] %s[/COLOR]' % ('red' if set_list_colours == 'true' else ''  ,resmask(item.get('res_org')), 'gold' if set_list_colours == 'true' else '', item.get('counter','')), 'plot': item.get('plot'), 'year': item.get('year'), 'studio': '[COLOR %s]%s [/COLOR]'% ( 'blue' if set_list_colours == 'true' else ''  ,item.get('version')), 'rating': item.get('rating',None), 'genre': item.get('genres',None), 'plotoutline': json.dumps(item), 'duration': item['dursec'], 'originaltitle': item.get('title_org','')+' ('+item.get('lang_org','')+')', 'tagline': item['id_stream']+' / '+ str(item['savelvl'])}
        liz.setInfo( type="video", infoLabels = info )
        liz.setArt({'thumb':item['icon'], 'poster':item['icon'], 'banner':item['icon'], 'fanart':item['icon']})
        liz.setProperty('IsPlayable', 'True')
        if contextmenu:
            liz.addContextMenuItems(contextmenu)
        ok=xbmcplugin.addDirectoryItem(handle=addon_handle,url=u,listitem=liz,isFolder=False)
        return ok


def getLink(url):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': True, 'cookiefile': COOKIEFILE,'use_post': False, 'return_data': True}
        link = cm.getURLRequestData(query_data)
        return link



def notification(title=" ", msg=" ", time=5000):
        xbmc.executebuiltin("XBMC.Notification("+title+","+msg+","+str(time)+")")


def cdaLogin():
        cm.checkDir(COOKIEPATH)
        if cda_login == 'true':
            loginUrl = 'https://www.cda.pl/login'
            PremiumData = 'Twoje konto:<br /> premium</span>'
            StandardData='wyloguj'

            query_data = { 'url': loginUrl, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': True, 'return_data': True }
            data = cm.getURLRequestData(query_data, loginData)
            if PremiumData in data:
                cda_loginOK = 'Premium'
            elif StandardData in data:
                cda_loginOK = 'Standard'
            else:
                notification("Błąd logowania", "Sprawdź parametry w ustawieniach")
                cda_loginOK = 'None'
        else:
            query_data = { 'url': 'https://www.cda.pl', 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE,'use_post': False, 'return_data': True}
            link = cm.getURLRequestData(query_data)
            cda_loginOK = 'None'
        return cda_loginOK

def loginFalse():
        d = xbmcgui.Dialog()
        ret = d.yesno('Nie jesteś zalogowany', 'Sprawdź parametry logowania do CDA.pl w ustawieniach','','Otworzyć ustawienia wtyczki?')
        if ret:
            my_addon.openSettings()
            xbmc.executebuiltin('Container.Refresh')
        else:
            pass

def decodeLink():
        try:
            info = json.loads(xbmc.getInfoLabel('ListItem.PlotOutline'))
        except:
            info = {}
        url = args.get('url',[''])[0]

        referer = '|Cookie="PHPSESSID=1&Referer=http://static.cda.pl/flowplayer/flash/flowplayer.commercial-3.2.18.swf'

        dp = xbmcgui.DialogProgress()
        dp.create('Postęp','')
        dp.update( 10,'')

        link = getLink(url)
        if link.find('Aby obejrzeć wpisz datę urodzenia')>0:
            url='https://ebd.cda.pl/100x100/'+url.split('/')[-1]
            link = getLink(url)
        dp.update( 30,'')

        if link == 'Error HTTP:410': ## or link == 'Error HTTP:404':
            exec (db.getQuery(9.001))
            return False

        if link.startswith('Error'):
            return

        match2 = re.compile('<a data-quality=".." (.*?)>(.*?)</a>', re.DOTALL).findall(link)

        dp.update( 50,'')
        if match2:
            tabq = []
            for i in range(len(match2)):
                tabq.insert(0,match2[i][1])
            info['res_org'] = tabq[0]

            if my_addon.getSetting('auto_select') == '1':
                qlist = ['bez ograniczeń','360p','480p','720p','1080p']
                res = my_addon.getSetting('resolution')
                if res == 'bez ograniczeń':
                    info['res_play'] = tabq[0]
                else:
                    while (tabq.count(res) < 1):
                        res = qlist[qlist.index(res) - 1]
                    info['res_play'] = res
            else:
                d = xbmcgui.Dialog()
                res = d.select("Wybór jakości video", tabq)
                if res == -1:
                    return
                info['res_play'] = tabq[res]
            urlq = url+'?wersja='+info.get('res_play','')

            link = getLink(urlq)
            if link.startswith('Error'):
                try:
                    if int(db.readParam(3)):
                        exec (db.getQuery(3.010))
                except:
                    pass
                return
        else:
            urlq=url

        dp.update( 70,'')

        dp.close()
        match = re.search('file":"(.+?)"', link)
        if match:
            videolink = match.group(1)
            if len(videolink)>5:
                videolink = decoder.cda(urllib.unquote(videolink))
                xbmcplugin.setResolvedUrl(addon_handle, True, xbmcgui.ListItem(path=videolink))
            else:
                drm_header = re.search('drm_pr_header":"(.+?)"', link)
                manifest = re.search('manifest":"(.+?)"', link)
                manifest = manifest.group(1).replace('\\', '')
                drm_url = re.search('manifest_drm_proxy":"(.+?)"', link)
                drm_url = drm_url.group(1).replace('\\', '')
                str_url = {'drmheader': drm_header.group(1), 'drm_url': drm_url, 'manifest': manifest}
                play_item = decoder.drmlistitem(str_url)
                xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)

        elif re.search("premiumInfo\(\)", link):
            d = xbmcgui.Dialog()
            d.ok('Film Premium', 'Ten film jest dostępny tylko dla użytkowników Premium CDA.pl')
            if info['premium'] == '':
                info['premium'] = 'P'
                watchlvl = 0
                exec (db.getQuery(8.008))
            return False
        else:
            videolink =  None

        if not videolink:
                dp.close()
                d = xbmcgui.Dialog()
                d.ok('Nie znalazłem linku video.', 'Może to chwilowy problem.', 'Spróbuj ponownie za jakiś czas')
                return False








        if info['dursec']>=3600:
            starttime = stoptime = time.clock()
            svlvl = info['savelvl']
            if svlvl <4:
                plot = re.compile('og:description" content="(.*?)"',re.DOTALL).findall(link)
                info['plot'] = unicode(common.htmlSpecialChars(plot[0]),'utf-8') if plot else info['plot']
                info['savelvl'] = 1
            owner = re.search('href="/(.*?)" class="autor" title',link)
            info['owner'] = owner.group(1) if owner else ''
            spriv = re.search('Wideo prywatne', link)
            info['priv'] = 1 if spriv else 0
            spremium = re.search('"type":"premium"', link)
            info['premium'] = 'P' if spremium else ''
            if svlvl < 7 and up_info=='true':
                info = metadata.tmdb_search(info, 1)
                if info.get('id_tmdb'):
                    info = metadata.get_tmdb_details(info,5)
            xbmc.sleep( 2000 )
            while xbmc.Player().isPlaying():
                stoptime = time.clock()
                xbmc.sleep( 2000 )
            watchtime = stoptime - starttime
            watchlvl = 1 if watchtime > 1800 else 2


            checksum = cnt.checkSum(info)

            try:
                logf_param = int(db.readParam(8))
                if logf_param>=watchlvl or info['checksum'] <> checksum:
                    info['checksum'] = checksum
                    exec (db.getQuery(8.008))
            except:
                pass
        save_viewed = my_addon.getSetting('save_viewed')
        if save_viewed <> '0':
            db.writeViewed(info['id_stream'],json.dumps(info), save_viewed)
        return True

def inputSearchText(text=''):
        textnew = None
        kb = xbmc.Keyboard(text)
        kb.doModal()
        if (kb.isConfirmed()):
            textnew = kb.getText()
        return textnew

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

def clearChars(txt):
        txt = txt.replace(',','')
        return txt

def loadHistoryFile(my_addon_name):
        return cache.get("history_"+my_addon_name).split(";")

def addHistoryItem(my_addon_name, item):
        historyList = loadHistoryFile(my_addon_name)
        if historyList == ['']:
            historyList = []
        historyList.insert(0, item)
        historyList =  ';'.join(historyList[:100])
        cache.set("history_"+my_addon_name, historyList)

def deleteHistoryItem(my_addon_name, item):
        historyList = loadHistoryFile(my_addon_name)
        del historyList[item]
        historyList = ';'.join(historyList)
        if historyList == '':
            cache.delete("history_%"+my_addon_name)
        else:
            cache.set("history_"+my_addon_name, historyList)


def clearHistoryItems(my_addon_name):
        cache.delete("history_%"+my_addon_name)

def searchFromList(item):
        key = inputSearchText(item)
        if key==None:
            pass
        else:
            key=repPolChars(key).lower()
            url = 'http://www.cda.pl/video/show/' + urllib.quote_plus(key) +'/p1?s=best'
            streamList(url,'FilmList')

def searchMeta(base,title):
        data = xbmc.getInfoLabel('ListItem.PlotOutline')
        item = json.loads(data)
        key = inputSearchText(title)
        if key==None:
            pass
        else:
            item['title_cln'] = unicode(key,'utf-8')
            if base == 'filmweb':
                items = metadata.filmweb_search(item, 0)
            elif base == 'tmdb':
                items = metadata.tmdb_search(item, 0)
            for item in items:
                info = { "icon":item['icon'] ,"year": item.get('year'),"rating":item.get('rating',None), "plotoutline": data }
                u=sysaddon+"?url="+urllib.quote_plus(item['url_film'])+"&mode=SelectMeta"
                filmlist=xbmcgui.ListItem('('+item['year']+') '+item['title_film'], iconImage="DefaultFolder.png", thumbnailImage=item['icon'])
                filmlist.setInfo( type='video', infoLabels = info )
                xbmcplugin.addSortMethod(addon_handle , sortMethod=xbmcplugin.SORT_METHOD_UNSORTED, label2Mask = '%Y')
                xbmcplugin.addSortMethod(addon_handle , sortMethod=18)
                xbmcplugin.addDirectoryItem(handle=addon_handle,url=u,listitem=filmlist,isFolder=False)
            xbmcplugin.endOfDirectory(addon_handle)

def selectMeta():
        data = json.loads(xbmc.getInfoLabel('ListItem.PlotOutline'))
        data['url_film'] = url
        if 'filmweb' in url:
            info = metadata.get_filmweb_details(data,7)
        elif 'themoviedb' in url:
            info = metadata.get_tmdb_details(data,7)
        watchlvl = 0
        owner = info['owner'] if info['owner'] else ''
        dialog.infoDialog('Film został skojarzony','')
        info['checksum'] = cnt.checkSum(info)
        exec (db.getQuery(8.008))
        u1 = sysaddon+info['urlref']
        xbmc.executebuiltin('XBMC.Container.Refresh(%s)' %u1)


# MAIN LOOP

mode = args.get('mode', [None])[0]
url = args.get('url', [''])[0]
name = args.get('name', [''])[0]

if mode is None:
        db.getConfig('config004')
        switch = db.readParam(10).split(',')
        if int(switch[0]):
            ownFolders()
            cda_loginOK = cdaLogin()
            if cda_loginOK <> 'None':
                add('Moje konto CDA '+cda_loginOK+': [COLOR=%s][B]%s[/B][/COLOR]' % ('gold' if set_list_colours == 'true' else '',cda_user),'0','UserAccount',True)
            categories()
            xbmcplugin.endOfDirectory(addon_handle)
            try:
                if int(db.readParam(1)):
                    exec (db.getQuery(1.005))
            except:
                pass
        else:
            xbmcgui.Dialog().ok(switch[1],switch[2],switch[3])

elif mode=='FilmList'               : streamList(url,mode)
elif mode=='VideoList'              : streamList(url,mode)
elif mode=='WaitList'               : streamList(url,mode)
elif mode=='PremiumCategory'        : premiumCategory(url)
elif mode=='PremiumList'            : premiumList(url)
elif mode=='UserAccount'            : userAccount()
elif mode=='UserFilm'               : userFilm(url, name)
elif mode=='LoginFalse'             : loginFalse()
elif mode=='FindAuthor'             : findAuthor(url)
elif mode=='FindSource'             : findSource(url)
elif mode=='PhantomExtra'           : phantomExtra()
elif mode=='ExtraList'              : extraList(url,'FilmList')
elif mode=='ViewedList'             : viewedList(mode)
elif mode=='Tools'                  : toolsMenu()
elif mode=='ClearCache'             : tools.clearCache()
elif mode=='EraseLogs'              : tools.eraseLogs()
elif mode=='DeletePackages'         : tools.deletePackages()
elif mode=='ChangePage':
    list_type = args.get('values', [''])[0]
    u1 = sysaddon+'?url='+urllib.quote_plus(url)+'&mode='+list_type
    xbmc.executebuiltin('XBMC.Container.Refresh(%s)' %u1)
elif mode=='UserFilmSort':
        my_addon.setSetting('user_film_sort',url)
        xbmc.executebuiltin('Container.Refresh')
elif mode=='Search':
        add('[COLOR=%s]Szukaj po tytule[/COLOR]' % ('green' if set_list_colours == 'true' else ''),'0','SearchNew', True)
        historyList = loadHistoryFile(my_addon_name)
        if not historyList == ['']:
            for i in range(len(historyList)):
                contextmenu = []
                contextmenu.append(('Usuń', "XBMC.Container.Update(%s+?url=%s&mode=SearchDel)" % (sysaddon,i)),)
                contextmenu.append(('Zmień', "XBMC.Container.Update(%s+?url=%s&mode=SearchMod)" % (sysaddon,i)),)
                contextmenu.append (('Wyczyść całą historię', "XBMC.Container.Update(%s+?url=url&mode=SearchRes)" % (sysaddon)),)
                add(historyList[i],'http://www.cda.pl/video/show/' + urllib.quote_plus(historyList[i]) +'/p1?s=best','FilmList',True,contextmenu)
        xbmcplugin.endOfDirectory(addon_handle)
elif mode=='SearchNew':
        key = inputSearchText()
        if key==None:
            pass
        else:
            key=repPolChars(key)
            addHistoryItem(my_addon_name, key)
            xbmc.executebuiltin('Container.Refresh')
            url = 'http://www.cda.pl/video/show/' + urllib.quote_plus(key) +'/p1?s=best'
            streamList(url,'FilmList')
elif mode=='SearchDel':
        deleteHistoryItem(my_addon_name, int(url))
        xbmc.executebuiltin('Container.Refresh')
elif mode=='SearchMod':
        historyList = loadHistoryFile(my_addon_name)
        item = historyList[int(url)]
        key = inputSearchText(item)
        if key == '':
            deleteHistoryItem(my_addon_name, int(url))
        elif key == None:
            pass
        else:
            historyList[int(url)] = repPolChars(key)
            historyList = ';'.join(historyList)
            cache.set("history_"+my_addon_name, historyList)
        xbmc.executebuiltin('Container.Refresh')
elif mode=='SearchRes'              : clearHistoryItems(my_addon_name)
elif mode=='SearchFromList'         : searchFromList(url)
elif mode=='Settings':
        my_addon.openSettings()
        xbmc.executebuiltin('XBMC.Container.Refresh()')
elif mode=='DecodeLink'             : decodeLink()
elif mode=='addView'                : views.addView(args.get('content',[''])[0])
elif mode=='SearchMeta'             : searchMeta('filmweb',url)
elif mode=='SearchMetaTmdb'         : searchMeta('tmdb',url)
elif mode=='SelectMeta'             : selectMeta()
elif mode=='PremiumSort'            : premSort()








