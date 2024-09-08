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
        ContentProvider.__init__(self, 'markiza.sk', 'https://www.markiza.sk/', username, password, filter, tmp_dir)
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
        result.append(self.dir_item('Relácie a seriály A-Z', self.base_url + 'relacie'))
        result.append(self.dir_item('Televízne noviny', self.base_url + 'relacie/televizne-noviny'))
        result.append(self.dir_item('TOP relácie', self.base_url + 'relacie#top'))
        result.append(self.dir_item('Najnovšie epizódy', self.base_url + 'relacie#latest'))
        item = self.video_item()
        item['title'] = 'Live Markiza'
        item['url'] = self.base_url + "live/1-markiza"
        item['img'] = "https://marhycz.github.io/picons/640/markiza.png"
        result.append(item)
        item = self.video_item()
        item['title'] = 'Live Doma'
        item['url'] = self.base_url + "live/3-doma"
        item['img'] = "https://marhycz.github.io/picons/640/doma.png"
        result.append(item)
        item = self.video_item()
        item['title'] = 'Live Dajto'
        item['url'] = self.base_url + "live/2-dajto"
        item['img'] = "https://marhycz.github.io/picons/640/dajto.png"
        result.append(item)
        item = self.video_item()
        item['title'] = 'Live Krimi'
        item['url'] = self.base_url + "live/22-krimi"
        item['img'] = "https://upload.wikimedia.org/wikipedia/commons/0/0a/Logo_Mark%C3%ADza_KRIMI.png"
        result.append(item)
        item = self.video_item()
        item['title'] = 'Live Klasik'
        item['url'] = self.base_url + "live/44-klasik"
        item['img'] = "https://www.tv-archiv.sk/images/tv/logo/markiza-klasik.jpg"
        result.append(item)
        return result

    def _resolve_live(self, item):
        resolved = []
        channel = item['url'].split('-')[-1]
        url = f'https://media.cms.markiza.sk/embed/{ channel }-live'
        httpdata = fetchUrl(url, self.opener)
        url = re.findall('(?:HLS|sources).*?"src":"([^"]+)"', httpdata)[0]
        url = url.replace('\\', '')
        item = self.video_item()
        item['surl'] = item['title']
        item['url'] = url + '|Referer=https://media.cms.markiza.sk/'
        resolved.append(item)
        return resolved

    def resolve(self, item, captcha_cb=None, select_cb=None):
       item = item.copy()
       if 'markiza.sk/live/' in item['url']:
           result = self._resolve_live(item)
       else:
           result = self._resolve_vod(item)
       if len(result) > 0 and select_cb:
           return select_cb(result)
       return result

    def list(self, url):
        self.info("list %s" % url)
        if url.endswith('relacie'):
            return self.list_show(url, list_series=True)
        elif url.endswith('top'):
            return self.list_top(url)
        elif url.endswith('latest'):
            return self.list_new(url)
        return self.list_show(url, list_episodes=True)
    
    def list_top(self, url):
        result = []
        doc = read_page(url)
        for article in doc.findAll('div', 'c-show-wrapper')[0].findAll('a', 'c-show'):
                item = self.dir_item()
                item['url'] = article['href']
                item['title'] = article['data-tracking-tile-show-name']
                item['img'] = article.div.img['data-src']
                result.append(item)
        return result
    
    def list_new(self, url):
        result = []
        doc = read_page(url)
        for article in doc.findAll('div', 'c-show-wrapper')[1].findAll('a', 'c-show'):
                item = self.dir_item()
                item['url'] = article['href']
                item['title'] = article['data-tracking-tile-show-name']
                item['img'] = article.div.img['data-src']
                result.append(item)
        return result
        
    def list_show(self, url, list_series=False, list_episodes=False):
        result = []
        if list_episodes:
           url+='/videa'
        self.info("list_show %s"%(url))
        print(('list_series: %s' % list_series))
        print(('list_episodes: %s' % list_episodes))
        try:
           doc = read_page(url)
        except urllib.error.HTTPError:
           xbmcgui.Dialog().ok('Error', 'CHYBA 404: STRÁNKA NEBOLA NÁJDENÁ')
           return
           
        if list_series:
            for article in doc.findAll('div', 'c-show-wrapper')[2].findAll('a', 'c-show'):
                item = self.dir_item()
                item['url'] = article['href']
                item['title'] = article['data-tracking-tile-show-name']
                item['img'] = article.div.img['data-src']
                result.append(item)
                                       
        if list_episodes:
                for article in doc.findAll('article', 'c-article'):
                    item = self.video_item()
                    item['url'] = article.a['href']
                    if 'markiza.sk/relacie/' in url and url.replace('/videa','') not in item['url']:
                        continue
                    item['title'] = article['data-tracking-tile-name'] 
                    item['img'] = article.a.picture.source['data-srcset']
                    result.append(item)
                button = doc.findAll('button', 'c-button -outline')
                if button:
                   item = self.dir_item()
                   item['url'] = button[0]['data-href']
                   item['title'] = button[0].span.text
                   result.append(item)
        return result

    def _resolve_vod(self, item):
        resolved = []
        doc = read_page(item['url'])
        main = doc.find('main')
        if (not main.find('iframe')):
           xbmcgui.Dialog().ok('Error', 'Platnosť tohoto videa už vypršala')
           return
        url = main.find('iframe')['data-src']
        httpdata = fetchUrl(url)
        httpdata = httpdata.replace("\r","").replace("\n","").replace("\t","")
        if '<title>Error</title>' in httpdata:
            error=re.search('<h2 class="e-title">(.*?)</h2>', httpdata).group(1) #Video nie je dostupné vo vašej krajine
            xbmcgui.Dialog().ok('Error', error)
            return

        url = re.search('\"sources\":\[{\"src\":\"(.+?)\"', httpdata)
        url = url.group(1).replace('\/','/')
         
        item = self.video_item()
        item['surl'] = item['title']
        item['url'] = url 
        resolved.append(item)    
    
        return resolved
        
