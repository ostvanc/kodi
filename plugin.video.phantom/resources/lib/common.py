# -*- coding: utf-8 -*-
import re


def htmlSpecialChars(txt):
        txt = txt.replace('#038;','')
        txt = txt.replace('<br />', '\n')
        txt = txt.replace('&lt;br/&gt;',' ')
        txt = txt.replace('&amp;rdquo;','"')
        txt = txt.replace('&amp;ndash;','-')
        txt = txt.replace('&bdquo;','"')
        txt = txt.replace('&raquo;','»').replace('&laquo;','«')
        txt = txt.replace('&rdquo;','"')
        txt = txt.replace('&rsquo;','\'')
        txt = txt.replace('&#34;','"')
        txt = txt.replace('&#39;','\'').replace('&#039;','\'').replace('&#x27;','\'')
        txt = txt.replace('&#8221;','"')
        txt = txt.replace('&#8222;','"')
        txt = txt.replace('&#8211;','-').replace('&ndash;','-')
        txt = txt.replace('&quot;','"').replace('&amp;quot;','"')
        txt = txt.replace('&oacute;','ó').replace('&Oacute;','Ó')
        txt = txt.replace('&amp;oacute;','ó').replace('&amp;Oacute;','Ó')
        txt = txt.replace('&eacute;','é')
        txt = txt.replace('&agrave;','à')
        txt = txt.replace('&middot;','·')
        txt = txt.replace('&amp;','&')
        txt = txt.replace('\u0105','ą').replace('\u0104','Ą')
        txt = txt.replace('\u0107','ć').replace('\u0106','Ć')
        txt = txt.replace('\u0119','ę').replace('\u0118','Ę')
        txt = txt.replace('\u0142','ł').replace('\u0141','Ł')
        txt = txt.replace('\u0144','ń').replace('\u0144','Ń')
        txt = txt.replace('\u00f3','ó').replace('\u00d3','Ó')
        txt = txt.replace('\u015b','ś').replace('\u015a','Ś')
        txt = txt.replace('\u017a','ź').replace('\u0179','Ź')
        txt = txt.replace('\u017c','ż').replace('\u017b','Ż')
        return txt

class count:
    def durSec(self, durtxt):
        duration = 0
        dur = durtxt.split(':')
        if len(durtxt) == 8:
            duration = int(dur[0])*3600+int(dur[1])*60+int(dur[2])
        elif len(durtxt) == 5:
            duration = int(dur[0])*60+int(dur[1])
        return duration

    def checkSum(self, info):
        version = info['version'][0] if info['version'] else ''
        checksums = info['res_org']+str(len(info['premium']))+str(info['priv'])+str(len(info['owner']))+version
        checksumf = str(len(info['title_stream']))+str(len(info['title_org']))+str(len(info['plot']))+str(len(info['icon']))+str(len(info.get('rating','')))+str(len(info.get('url_film','')))+info.get('year','')+str(len(info.get('genres','')))
        checksum = checksumf+'_'+checksums
        return checksum

