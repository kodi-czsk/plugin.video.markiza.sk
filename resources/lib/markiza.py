# -*- coding: UTF-8 -*-
# /*
# *      Copyright (C) 2014 Maros Ondrasek
# *
# *
# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with this program; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# *
# */

import http.cookiejar
import urllib.request, urllib.parse, urllib.error
import re
from datetime import date
import xbmcgui
import util
from provider import ContentProvider
from bs4 import BeautifulSoup, BeautifulStoneSoup


_UserAgent_ = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0'
loginurl = 'https://moja.markiza.sk/'

#handle Sectigo CA cert missing in cacerts - disable SSL checks
try:
   import ssl
   ssl._create_default_https_context = ssl._create_unverified_context
except:
   pass

def fetchUrl(url, opener=None, ref=None):
        httpdata = ''	           
        req = urllib.request.Request(url)
        req.add_header('User-Agent', _UserAgent_)
        if ref:
            req.add_header('Referer', ref)
        if opener:
            resp = opener.open(req)
        else:
            resp = urllib.request.urlopen(req)
        httpdata = resp.read().decode('utf-8')
        resp.close()
        return httpdata

def read_page(url):
    return BeautifulSoup(fetchUrl(url), "html5lib")

class markizaContentProvider(ContentProvider):

    def __init__(self, username=None, password=None, filter=None, tmp_dir='/tmp'):
        ContentProvider.__init__(self, 'markiza.sk', 'https://videoarchiv.markiza.sk/', username, password, filter, tmp_dir)
        self.cp = urllib.request.HTTPCookieProcessor(http.cookiejar.LWPCookieJar())
        self.init_urllib()

    def init_urllib(self):
        # workaround insecure connection to moja.markiza.sk
        ctx_no_secure = ssl.create_default_context()
        ctx_no_secure.set_ciphers('HIGH:!DH:!aNULL')
        ctx_no_secure.check_hostname = False
        ctx_no_secure.verify_mode = ssl.CERT_NONE

        opener = urllib.request.build_opener(self.cp, urllib.request.HTTPSHandler(context=ctx_no_secure))
        self.opener = opener
        urllib.request.install_opener(opener)

    def capabilities(self):
        return ['categories', 'resolve', '!download']
            
    def categories(self):
        result = []
        result.append(self.dir_item('Relácie a seriály A-Z', self.base_url + 'relacie-a-serialy'))
        result.append(self.dir_item('Televízne noviny', self.base_url + 'video/televizne-noviny'))
        result.append(self.dir_item('TOP relácie', 'top' ))
        result.append(self.dir_item('Najnovšie epizódy', 'new' ))
 
        item = self.video_item()
        item['title'] = 'Live Markiza'
        item['url'] = self.base_url + "live/1-markiza"
        item['img'] = "DefaultVideo.png"
        result.append(item)
        item = self.video_item()
        item['title'] = 'Live Doma'
        item['url'] = self.base_url + "live/3-doma"
        item['img'] = "DefaultVideo.png"
        result.append(item)
        item = self.video_item()
        item['title'] = 'Live Dajto'
        item['url'] = self.base_url + "live/2-dajto"
        item['img'] = "DefaultVideo.png"
        result.append(item)
        return result

    def list(self, url):
        self.info("list %s" % url)
        if 'relacie-a-serialy' in url:
            return self.list_show(url, list_series=True)
        elif 'top' == url:
            return self.list_top(self.base_url)
        elif 'new' == url:
            return self.list_new(self.base_url)
        return self.list_show(url, list_episodes=True)
    
    def list_top(self, url):
        result = []
        doc = read_page(url)
        for section in doc.findAll('section', 'b-main-section my-5'):
            if section.div.h3.getText(" ") == 'TOP RELÁCIE':
                for article in section.findAll('article'):
                    item = self.dir_item()
                    item['url'] = article.a['href']
                    item['title'] = article.a['title']
                    item['img'] = article.a.div.img['data-original']
                    result.append(item)
        return result\
    
    def list_new(self, url):
        result = []
        doc = read_page(url)
        for section in doc.findAll('section', 'b-main-section'):
            if section.div.h3 and section.div.h3.getText(" ") == 'NAJNOVŠIE EPIZÓDY':
                    for article in section.div.div.findAll('article'):
                        item = self.video_item()
                        item['url'] = article.a['href']
                        item['title'] = article.a.find('div', {'class': 'e-info'}).getText(" ")
                        item['title'] = " ".join(item['title'].split())
                        item['img'] = article.a.div.img['data-original']
                        result.append(item)
        return result
        
    def list_show(self, url, list_series=False, list_episodes=False):
        result = []
        self.info("list_show %s"%(url))
        print(('list_series: %s' % list_series))
        print(('list_episodes: %s' % list_episodes))
        try:
           doc = read_page(url)
        except urllib.error.HTTPError:
           xbmcgui.Dialog().ok('Error', 'CHYBA 404: STRÁNKA NEBOLA NÁJDENÁ')
           return
           
        if list_series:
            for article in doc.findAll('article'):
                item = self.dir_item()
                item['url'] = article.a['href']
                item['title'] = article.a['title']
                item['img'] = article.a.div.img['data-original']
                result.append(item)
                                       
        if list_episodes:
                for article in doc.findAll('article', 'b-article b-article-text b-article-inline'):
                    item = self.video_item()
                    item['url'] = article.a['href']
                    if self.base_url not in item['url']:
                        continue
                    item['title'] = article.a.find('div', {'class': 'e-info'}).getText(" ")
                    item['title'] = " ".join(item['title'].split())
                    item['img'] = article.a.div.img['data-original']
                    result.append(item)

                for section in doc.findAll('section', 'b-main-section'):
                    if section.div.h3.getText(" ") == 'Celé epizódy':
                        for article in section.findAll('article'):
                            item = self.video_item()
                            item['url'] = article.a['href']
                            if self.base_url not in item['url']:
                                continue
                            if (article.a.find('div', {'class': 'e-date'})):
                               item['title'] = 'Celé epizódy - ' + article.a.find('div', {'class': 'e-info'}).getText(" ")
                            else:
                               item['title'] = 'Celé epizódy - ' + article.a['title']
                            item['title'] = " ".join(item['title'].split())
                            item['img'] = article.a.div.img['data-original']
                            result.append(item)

                    if section.div.h3.getText(" ") == 'Mohlo by sa vám páčiť':
                        for article in section.findAll('article'):
                            item = self.video_item()
                            item['url'] = article.a['href']
                            if self.base_url not in item['url']:
                                continue
                            item['title'] = 'Mohlo by sa vám páčiť - ' + article.a.find('div', {'class': 'e-info'}).getText(" ")
                            item['title'] = " ".join(item['title'].split())
                            item['img'] = article.a.div.img['data-original']
                            result.append(item)

                    if section.div.h3.getText(" ") == 'Zo zákulisia':
                        for article in section.findAll('article'):
                            item = self.video_item()
                            item['url'] = article.a['href']
                            if self.base_url not in item['url']:
                                continue
                            item['title'] = 'Zo zákulisia - ' + article.a['title']
                            item['title'] = " ".join(item['title'].split())
                            item['img'] = article.a.div.img['data-original']
                            result.append(item)
        return result

    def resolve(self, item, captcha_cb=None, select_cb=None):
       item = item.copy()
       if 'markiza.sk/live/' in item['url']:
           result = self._resolve_live(item, relogin=True)
       else:
           result = self._resolve_vod(item)
       if len(result) > 0 and select_cb:
           return select_cb(result)
       return result

    def _resolve_vod(self, item):
        resolved = []
        doc = read_page(item['url'])
        main = doc.find('main')
        if (not main.find('iframe')):
           xbmcgui.Dialog().ok('Error', 'Platnost tohoto videa už vypršala')
           return
        url = main.find('iframe')['src']
        httpdata = fetchUrl(url)
        httpdata = httpdata.replace("\r","").replace("\n","").replace("\t","")
        if '<title>Error</title>' in httpdata:
            error=re.search('<h2 class="e-title">(.*?)</h2>', httpdata).group(1) #Video nie je dostupné vo vašej krajine
            xbmcgui.Dialog().ok('Error', error)
            return

        url = re.search('\"HLS\":\[{\"src\":\"(.+?)\"', httpdata)
        url = url.group(1).replace('\/','/')
         
        thumb = re.search('<meta property="og:image" content="(.+?)">', httpdata)
        thumb = thumb.group(1) if thumb else ''
        name = re.search('<meta property="og:title" content="(.+?)">', httpdata)
        name = name.group(1) if name else '?'
        desc = re.search('<meta name="description" content="(.+?)">', httpdata)
        desc = desc.group(1) if desc else name

        httpdata = fetchUrl(url)

        streams = re.compile('RESOLUTION=\d+x(\d+).*\n([^#].+)').findall(httpdata) 
        url = url.rsplit('/', 1)[0] + '/'
        for (bitrate, stream) in streams:
            item = self.video_item()
            item['surl'] = item['title']
            item['quality'] = bitrate.replace('432','480')
            item['url'] = url + stream
            item['img'] = thumb
            resolved.append(item)
        resolved = sorted(resolved, key=lambda x:int(x['quality']), reverse=True)
        for idx, item in enumerate(resolved):
           item['quality'] += 'p'
        return resolved

    def _resolve_live(self, item, relogin=False):
        resolved = []
        if not (self.username and self.password):
            xbmcgui.Dialog().ok('Error', 'Nastavte prosím moja.markiza.sk konto')
            return
        if relogin:
           httpdata = fetchUrl(loginurl, self.opener)
           token = re.search(r'name=\"_token_\" value=\"(\S+?)\">',httpdata).group(1)
           logindata = urllib.parse.urlencode({'email': self.username, 'password': self.password  , '_token_': token, '_do': 'content1-loginForm-form-submit', 'login': 'Prihl%C3%A1si%C5%A5+sa' }).encode('utf-8')
           req = urllib.request.Request(loginurl, logindata)
           httpdata = self.opener.open(req)
           
        httpdata = fetchUrl(item['url'], self.opener)
        url = re.search(r'<iframe src=\"(https:\/\/videoarchiv\S+?)\"',httpdata).group(1) #https://videoarchiv.markiza.sk/api/v1/user/live
        url = url.replace('&amp;','&')    
        httpdata = fetchUrl(url, self.opener)
        if '<iframe src=\"' not in httpdata:   #handle expired cookies
           if relogin:
              xbmcgui.Dialog().ok('Error', 'Skontrolujte prihlasovacie údaje')
              return 
           else:
              return self._resolve_live(item, relogin=True) 
     
        referer=url
        url = re.search(r'<iframe src=\"(https:\/\/media\S+?)\"',httpdata).group(1) #https://media.cms.markiza.sk/embed/
        httpdata = fetchUrl(url,self.opener,referer) 
        if '<title>Error</title>' in httpdata:
            error=re.search('<h2 class="e-title">(.*?)</h2>', httpdata).group(1) #Video nie je dostupné vo vašej krajine
            xbmcgui.Dialog().ok('Error', error)
            return 
        url = re.search(r'\"src\":\"(\S+?)\"',httpdata).group(1).replace('\/','/') #https:\/\/cmesk-ott-live-sec.ssl.cdn.cra.cz
        httpdata = fetchUrl(url,self.opener,'https://media.cms.markiza.sk/')
 
        streams = re.compile('RESOLUTION=\d+x(\d+).*\n([^#].+)').findall(httpdata)   
        url = url.rsplit('/', 1)[0] + '/'
        for (bitrate, stream) in streams:
            item = self.video_item()
            item['surl'] = item['title']
            item['quality'] = bitrate.replace('432','480').replace('640','720')   #adjust to predefined 360p, 480p and 720p
            item['url'] = url + stream + '|Referer=https://media.cms.markiza.sk/'
            resolved.append(item)
        resolved = sorted(resolved, key=lambda x:int(x['quality']), reverse=True)
        for idx, item in enumerate(resolved):
           item['quality'] += 'p'
        return resolved
