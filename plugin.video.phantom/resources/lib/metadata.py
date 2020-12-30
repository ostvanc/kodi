# -*- coding: utf-8 -*-

import re,os, sys, time, json
import xbmc, xbmcgui
import urllib, urllib2

import db, PhantomCommon, common
cm      = PhantomCommon.common()
cnt     = common.count()

headers = {'User-Agent': db.readParam(9),}

def log(msg): xbmc.log(msg,level=xbmc.LOGNOTICE)

def getMeta(items):
    idlist = []
    for item in items:
        idlist.append(item['id_stream'])
    idlist = str(idlist)
    exec (db.getQuery(4.008))
    data = re.compile('ids=(.*?),items=(.*?)koniec_meta', flags=re.S).findall(response)
    ids = json.loads(data[0][0]) if data else ''
    infos = json.loads(data[0][1]) if data else ''
    dp = xbmcgui.DialogProgressBG()
    dp.create('','')
    itemslen = len(items)
    for i in range(itemslen):
        id_stream = items[i]['id_stream']
        if id_stream in ids:
            dursec = items[i]['dursec']
            idx = ids.index(id_stream)
            items[i] = infos[idx]
            items[i]['dursec'] = dursec
        elif items[i]['dursec']>=3600:
            dp.update(i*100/itemslen,str(i+1)+'/'+str(itemslen),items[i]['title_stream'].encode("utf-8"))
            info = tmdb_search(items[i], 1)
            watchlvl = 0
            res_play = ''
            owner = ''
            info['checksum'] = cnt.checkSum(info)
            exec (db.getQuery(8.008))
            items[i] = info
    dp.close()
    return items

def filmweb_search(item, par):
    items = []
    search_url = 'http://www.filmweb.pl/films/search?q=%s' % urllib.quote_plus(item['title_cln'].encode("utf-8"))
    link = getLink(search_url)
    results = re.compile('filmPreview--FILM(.*?)</div></div></div></div>').findall(link)
    for result in results:
        id_film = re.search('data-id="(.*?)"', result)
        icon = re.search('data-image="(.*?)"', result)
        url_film = re.search('filmPreview__link" href="(.*?)"', result)
        title = re.search('title="(.*?)"', result)
        year = re.search('Year">(.*?)<', result)
        rating = re.search('rateBox__rate">(.*?)<', result)
        rating = rating.group(1).replace(',','.') if rating else ''
        if icon:
            items.append({'id_film':id_film.group(1), 'icon':icon.group(1).replace('.6.jpg','.3.jpg'), 'url_film':'http://www.filmweb.pl'+url_film.group(1), 'title_film':common.htmlSpecialChars(title.group(1)), 'year':year.group(1), 'rating' : rating})
    if par == 0:
        return items
    elif par == 1:
        counter = len(items)
        for pitem in items:
            title_u = unicode(pitem['title_film'],'utf-8')
            if counter == 1 or item['year'] == pitem['year']:
                item['id_film'] = pitem['id_film']
                item['url_film'] = pitem['url_film']
                item['title_stream'] = title_u
                item['title_cln'] = title_u
                item['year'] = pitem['year']
                item['icon'] = pitem['icon']
                item['rating'] = pitem['rating']
                item['savelvl'] = 3
                break
        return item


def get_filmweb_details(item, savelvl):
    url = item.get('url_film')
    link = getLink(url)
    data = re.compile('{"id":(.*?),(.*?)title":"(.*?)"(.*?)year":(.*?),').findall(link)
    rating = re.search('ratingValue"> (.*?)<', link)
    item['rating'] = rating.group(1).replace(',','.') if rating else ''
    plot = re.compile('itemprop="description">(.{4,}?)</').findall(link)
    if plot:
        item['plot'] = unicode(common.htmlSpecialChars(plot[0].replace('<span class="fullText hide">','')),'utf-8')
    icon = re.search('og:image" content="(.*?)"', link)
    if icon:
        item['icon'] = icon.group(1)
    gen = re.search('genre">(.*?)"filmInfo', link)
    genres = str(re.compile('ranking/film/.*?">(.*?)<').findall(gen.group(1))).replace('[','').replace(']','').replace("'","")
    item['id_film'] = data[0][0]
    title_u = unicode(data[0][2],'utf-8')
    item['title_stream'] = title_u
    item['title_cln'] = title_u
    item['year'] = data[0][4]
    item['genres'] = genres.replace('\\xc5\\x82','ł')
    item['savelvl'] = 3 if item['id_tmdb'] == '' else 7
    return item

def tmdb_search(item, par):
    items = []
    search_url = 'https://www.themoviedb.org/search/movie?query=%s&language=pl-PL' % urllib.quote_plus(item['title_cln'].encode("utf-8"))
    link = getLink(search_url)
    results = re.compile('div id="card(.*?)\\n      </div>\\n    </div>\\n  </div>\\n\\n  \\n</div>', re.DOTALL).findall(link)
    for result in results:
        url_film = re.search('/movie/(.*?)\?language=pl-PL', result)
        icon = re.search('1x, (.*?) 2x', result)
        plot = re.search('<p>(.*?)<', result)
        plot = unicode(common.htmlSpecialChars(plot.group(1)),'utf-8') if plot else ''
        title = re.search('alt="(.*?)"', result)
        syear = re.search('release_date">(.*?)<', result)
        year = syear.group(1)[-4:] if syear else ''
        if icon:
            icon = icon.group(1).replace('w188_and_h282_bestv2','w500')
            icon = 'https:'+icon
            items.append({'id_tmdb':url_film.group(1), 'icon':icon, 'url_film':'https://www.themoviedb.org'+url_film.group(0), 'title_film':common.htmlSpecialChars(title.group(1)), 'year':year, 'plot': plot})
    if par == 0:
        return items
    elif par == 1:
        counter = len(items)
        for pitem in items:
            title_u = unicode(pitem['title_film'],'utf-8')
            if counter == 1 or item['year'] == pitem['year']:
                item['id_tmdb'] = pitem['id_tmdb']
                item['url_film'] = pitem['url_film']
                item['title_stream'] = title_u
                item['title_cln'] = title_u
                item['year'] = pitem['year']
                item['icon'] = pitem['icon']
                item['plot'] = pitem['plot']
                item['rating'] = '' ##pitem['rating']
                item['savelvl'] = 4
                break
        return item

def get_tmdb_details(item, savelvl):
    url = item.get('url_film')
    link = getLink(url)
    id_tmdb = re.search('movie/(.*?)\?', url)
    title = re.search('<title>(.*?) \((\d{4})\)', link)
    title_u = unicode(common.htmlSpecialChars(title.group(1)),'utf-8')
    title_org = re.search('Oryginalny tytuł</strong> (.*?)<', link)
    lang_org = re.search('Oryginalny język</bdi></strong> (.*?)<', link)
    icon = re.search('og:image" content="(.*?)"', link)
    plot = re.compile('Opis</h3.*?p>(.*?)<', re.DOTALL).findall(link)
    rating = re.search('data-percent="(.*?)\.', link)
    rt = rating.group(1)
    genres = str(re.compile('genre/.*?">(.*?)<').findall(link)).replace('[','').replace(']','').replace("'","")
    item['plot'] = unicode(common.htmlSpecialChars(plot[0]),'utf-8')
    item['id_tmdb'] = id_tmdb.group(1)
    item['title_stream'] = title_u.rstrip()
    item['title_cln'] = title_u.rstrip()
    item['title_org'] = unicode(common.htmlSpecialChars(title_org.group(1)),'utf-8') if title_org else item['title_stream']
    item['lang_org'] = unicode(common.htmlSpecialChars(lang_org.group(1)),'utf-8') if lang_org else ''
    item['icon'] = 'https:'+icon.group(1)
    item['year'] = title.group(2)
    item['rating'] = rt[0]+'.'+rt[1] if len(rt)==2 else '0.0'
    item['genres'] = genres.replace('\\xc5\\x82','ł')
    item['savelvl'] = savelvl
    return item

def getLink(url):
        req = urllib2.Request(url, None, headers)
        try:
            response = urllib2.urlopen(req,timeout = 10)
            link=response.read()
            response.close()
        except:
            link=''
        return link
