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

    def _resolve_live(self, item):
        resolved = []
        channel = item['url'].split('-')[-1]
        url = f'https://media.cms.markiza.sk/embed/{ channel }-live'
        httpdata = fetchUrl(url, self.opener)
        url = re.findall('HLS.*?"src":"([^"]+)"', httpdata)[0]
        url = url.replace('\\', '')
        item = self.video_item()
        item['surl'] = item['title']
        item['url'] = url + '|Referer=https://media.cms.markiza.sk/'
        resolved.append(item)
        return resolved

    def resolve(self, item, captcha_cb=None, select_cb=None):
       item = item.copy()
       result = self._resolve_live(item)
       if len(result) > 0 and select_cb:
           return select_cb(result)
       return result
