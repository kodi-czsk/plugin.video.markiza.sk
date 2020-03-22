# -*- coding: utf-8 -*-
import urllib2,urllib,re,os
import json
from parseutils import *
from stats import *
import xbmcplugin,xbmcgui,xbmcaddon
from cookielib import CookieJar

__baseurl__ = 'http://videoarchiv.markiza.sk'
_UserAgent_ = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0'
addon = xbmcaddon.Addon('plugin.video.markiza.sk')
profile = xbmc.translatePath(addon.getAddonInfo('profile'))
__settings__ = xbmcaddon.Addon(id='plugin.video.markiza.sk')
home = __settings__.getAddonInfo('path')
icon = xbmc.translatePath( os.path.join( home, 'icon.png' ) )
fanart = xbmc.translatePath( os.path.join( home, 'fanart.jpg' ) )
loginurl = 'https://moja.markiza.sk/'

#Nacteni informaci o doplnku
__addon__      = xbmcaddon.Addon()
__addonname__  = __addon__.getAddonInfo('name')
__addonid__    = __addon__.getAddonInfo('id')
__cwd__        = __addon__.getAddonInfo('path').decode("utf-8")
__language__   = __addon__.getLocalizedString
__set__ = __addon__.getSetting

settings = {'username': __set__('markiza_user'), 'password': __set__('markiza_pass')}

def log(msg):
    xbmc.log(("### [%s] - %s" % (__addonname__.decode('utf-8'), msg.decode('utf-8'))).encode('utf-8'), level=xbmc.LOGDEBUG)

def fetchUrl(url):
    log("fetchUrl " + url)
    httpdata = ''	
    req = urllib2.Request(url)
    req.add_header('User-Agent', _UserAgent_)
    resp = urllib2.urlopen(req)
    httpdata = resp.read()
    resp.close()
    return httpdata


def OBSAH():
    addDir('Relácie a seriály A-Z','http://videoarchiv.markiza.sk/relacie-a-serialy',5,icon,1)
    addDir('Televízne noviny','http://videoarchiv.markiza.sk/video/televizne-noviny',2,icon,1)
    addDir('TOP relácie','http://videoarchiv.markiza.sk',9,icon,1)
    addDir('Najnovšie epizódy','http://videoarchiv.markiza.sk',8,icon,1)
    addLive('LIVE Markiza','https://videoarchiv.markiza.sk/live/1-markiza',10,icon,1)
    addLive('LIVE Doma','https://videoarchiv.markiza.sk/live/3-doma',10,icon,1)
    addLive('LIVE Dajto','https://videoarchiv.markiza.sk/live/2-dajto',10,icon,1)
  #  addDir('Najsledovanejšie','http://videoarchiv.markiza.sk',6,icon,1)
  #  addDir('Odporúčame','http://videoarchiv.markiza.sk',7,icon,1)

def HOME_NEJSLEDOVANEJSI(url,page):
    doc = read_page(url)

    for section in doc.findAll('section', 'b-main-section b-section-articles b-section-articles-primary my-5'):
        if section.div.h3.getText(" ").encode('utf-8') == 'Najsledovanejšie':
            for article in section.findAll('article'):
                url = article.a['href'].encode('utf-8')
                title = article.a.find('div', {'class': 'e-text-row'}).getText(" ").encode('utf-8')
                thumb = article.a.div.img['data-original'].encode('utf-8')
                addDir(title,url,3,thumb,1)

def HOME_DOPORUCUJEME(url,page):
    doc = read_page(url)

    for section in doc.findAll('section', 'b-main-section b-section-articles b-section-articles-primary my-5'):
        if section.div.h3.getText(" ").encode('utf-8') == 'Odporúčame':
            for article in section.findAll('article'):
                url = article.a['href'].encode('utf-8')
                title = article.a.find('div', {'class': 'e-info'}).getText(" ").encode('utf-8')
                thumb = article.a.div.img['data-original'].encode('utf-8')
                addDir(title,url,3,thumb,1)

def HOME_POSLEDNI(url,page):
    doc = read_page(url)

    for section in doc.findAll('section', 'b-main-section'):
        if section.div.h3 and section.div.h3.getText(" ").encode('utf-8') == 'Najnovšie epizódy':
            for article in section.findAll('article'):
                url = article.a['href'].encode('utf-8')
                title = article.a.find('div', {'class': 'e-info'}).getText(" ").encode('utf-8')
                thumb = article.a.div.img['data-original'].encode('utf-8')
                addDir(title,url,3,thumb,1)

def HOME_TOPPORADY(url,page):
    doc = read_page(url)

    for section in doc.findAll('section', 'b-main-section my-5'):
        if section.div.h3.getText(" ").encode('utf-8') == 'TOP relácie':
            for article in section.findAll('article'):
                url = article.a['href'].encode('utf-8')
                title = article.a['title'].encode('utf-8')
                thumb = article.a.div.img['data-original'].encode('utf-8')
                addDir(title,url,2,thumb,1)

def CATEGORIES(url,page):
    print 'CATEGORIES *********************************' + str(url)
    doc = read_page(url)

    for article in doc.findAll('article'):
        url = article.a['href'].encode('utf-8')
        title = article.a['title'].encode('utf-8')
        thumb = article.a.div.img['data-original'].encode('utf-8')
        addDir(title,url,2,thumb,1)

def EPISODES(url,page):
    print 'EPISOD9ES *********************************' + str(url)
    doc = read_page(url)

    for article in doc.findAll('article', 'b-article b-article-text b-article-inline'):
        url = article.a['href'].encode('utf-8')
        title = article.a.find('div', {'class': 'e-info'}).getText(" ").encode('utf-8').strip() 
        thumb = article.a.div.img['data-original'].encode('utf-8')
        addDir(title,url,3,thumb,1)

    for section in doc.findAll('section', 'b-main-section'):
        if section.div.h3.getText(" ").encode('utf-8') == 'Celé epizódy':
            for article in section.findAll('article'):
                url = article.a['href'].encode('utf-8')
                if (article.a.find('div', {'class': 'e-date'})):
                   title = 'Celé epizódy - ' + article.a.find('div', {'class': 'e-info'}).getText(" ").encode('utf-8')
                else:
                   title = 'Celé epizódy - ' + article.a['title'].encode('utf-8')
                thumb = article.a.div.img['data-original'].encode('utf-8')
                addDir(title,url,3,thumb,1)

        if section.div.h3.getText(" ").encode('utf-8') == 'Mohlo by sa vám páčiť':
            for article in section.findAll('article'):
                url = article.a['href'].encode('utf-8')
                title = 'Mohlo by sa vám páčiť - ' + article.a.find('div', {'class': 'e-info'}).getText(" ").encode('utf-8') 
                thumb = article.a.div.img['data-original'].encode('utf-8')
                addDir(title,url,3,thumb,1)

        if section.div.h3.getText(" ").encode('utf-8') == 'Zo zákulisia':
            for article in section.findAll('article'):
                url = article.a['href'].encode('utf-8')
                title = 'Zo zákulisia - ' + article.a['title'].encode('utf-8')
                thumb = article.a.div.img['data-original'].encode('utf-8')
                addDir(title,url,3,thumb,1)
                
def VIDEOLINK(url,name):
    print 'VIDEOLINK *********************************' + str(url)

    doc = read_page(url)
    main = doc.find('main')
    if (not main.find('iframe')):
       xbmcgui.Dialog().ok('Chyba', 'Platnost tohoto videa už vypršala', '', '')
       return False
    url = main.find('iframe')['src']
    httpdata = fetchUrl(url)
    httpdata = httpdata.replace("\r","").replace("\n","").replace("\t","")

    url = re.search('src = {\s*\"hls\": [\'\"](.+?)[\'\"]\s*};', httpdata)
    if (url):
       url=url.group(1)

       thumb = re.search('<meta property="og:image" content="(.+?)">', httpdata)
       thumb = thumb.group(1) if thumb else ''

       desc = re.search('<meta name="description" content="(.+?)">', httpdata)
       desc = desc.group(1) if desc else ''

       name = re.search('<meta property="og:title" content="(.+?)">', httpdata)
       name = name.group(1) if name else '?'

       httpdata = fetchUrl(url)

       streams = re.compile('RESOLUTION=\d+x(\d+).*\n([^#].+)').findall(httpdata) 
       url = url.rsplit('/', 1)[0] + '/'
       streams.sort(key=lambda x: int(x[0]),reverse=True)
       for (bitrate, stream) in streams:
           bitrate=' [' + bitrate + 'p]'
           addLink(name + bitrate,url + stream,thumb,desc)

    else:
       #televizne noviny
       url = re.search('relatedLoc: [\'\"](.+?)[\'\"]', httpdata).group(1)
       url = url.replace("\/","/")
       
       httpdata = fetchUrl(url)
       
       decoded=json.loads(httpdata)
       for chapter in decoded["playlist"]:
          name=chapter["contentTitle"]
          url=chapter["src"]["hls"]
          url=url.rsplit('/', 1)[0] + '/' + 'index-f3-v1-a1.m3u8' #auto select 720p quality
          thumb=chapter.get("thumbnail",'')
          desc=chapter["contentTitle"]
          addLink(name,url,thumb,desc)

def live(url, page):
    if not (settings['username'] and settings['password']):
        xbmcgui.Dialog().ok('Chyba', 'Nastavte prosím Markíza konto', '', '')
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), False, xbmcgui.ListItem())
        raise RuntimeError
    cj = CookieJar()	
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    response = opener.open(loginurl).read()
    token = re.search(r'name=\"_token_\" value=\"(\S+?)\">',response).group(1)
    data = urllib.urlencode({'email': settings['username'], 'password': settings['password'], '_token_': token, '_do': 'content1-loginForm-form-submit' })
    data+='&login=Prihl%C3%A1si%C5%A5+sa'
    opener.open(loginurl, data) 
   
    response = opener.open(url).read()
    url = re.search(r'<iframe src=\"(\S+?)\"',response).group(1) #https://videoarchiv.markiza.sk/api/v1/user/live
    response = opener.open(url).read()
    opener.addheaders = [('Referer',url)]
    url = re.search(r'<iframe src=\"(\S+?)\"',response).group(1) #https://media.cms.markiza.sk/embed/
    response = opener.open(url).read()
    url = re.search(r'\"hls\": \"(\S+?)\"',response).group(1) #https://h1-s6.c.markiza.sk/hls/markiza-sd-master.m3u8
    response = opener.open(url).read()
    
    cookies='|Cookie='
    for cookie in cj:
      cookies+=cookie.name+'='+cookie.value+';'
    cookies=cookies[:-2]
    play_item = xbmcgui.ListItem(path=url+cookies)
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem=play_item)
	
def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]

        return param

def addLink(name,url,iconimage,popis):
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": popis} )
        liz.setProperty( "Fanart_Image", fanart )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok

def addDir(name,url,mode,iconimage,page):
        if ("voyo.markiza.sk" in url):
           return False 
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&page="+str(page)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        liz.setProperty( "Fanart_Image", fanart )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok
		
def addLive(name,url,mode,iconimage,page):
        if ("voyo.markiza.sk" in url):
           return False 
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&page="+str(page)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        liz.setProperty( "Fanart_Image", fanart )
        liz.setProperty('IsPlayable', 'true')
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
        return ok

params=get_params()
url=None
name=None
thumb=None
mode=None
page=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass
try:
        page=int(params["page"])
except:
        pass

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)
print "Page: "+str(page)

if mode==None or url==None or len(url)<1:
        STATS("OBSAH", "Function")
        OBSAH()

elif mode==6:
        STATS("HOME_NEJSLEDOVANEJSI", "Function")
        HOME_NEJSLEDOVANEJSI(url,page)

elif mode==7:
        STATS("HOME_DOPORUCUJEME", "Function")
        HOME_DOPORUCUJEME(url,page)

elif mode==8:
        STATS("HOME_POSLEDNI", "Function")
        HOME_POSLEDNI(url,page)

elif mode==9:
        STATS("HOME_TOPPORADY", "Function")
        HOME_TOPPORADY(url,page)

elif mode==5:
        STATS("CATEGORIES", "Function")
        CATEGORIES(url,page)

elif mode==2:
        STATS("EPISODES", "Function")
        EPISODES(url,page)

elif mode==3:
        STATS("VIDEOLINK", "Function")
        VIDEOLINK(url,page)

elif mode==10:
        STATS("LIVE", "Function")
        live(url,page)


xbmcplugin.endOfDirectory(int(sys.argv[1]))
