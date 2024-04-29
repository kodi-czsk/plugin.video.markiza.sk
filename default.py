    # -*- coding: UTF-8 -*-
#/*
# *      Copyright (C) 2013 Maros Ondrasek
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
import os
sys.path.append( os.path.join ( os.path.dirname(__file__),'resources','lib') )
import markiza
from epg_sms import get_sms_epg
import xbmcprovider,xbmcaddon
import util
from urllib.parse import urlencode, parse_qsl

import json
import socket

class IPTVManager:
    """Interface to IPTV Manager"""

<<<<<<< HEAD
<<<<<<< HEAD
    def __init__(self, port,channels):
        """Initialize IPTV Manager object"""
        self.port = port
        self.channels = channels
=======
    def __init__(self, port, channels, epgdays=3, epgdaysback=1):
        """Initialize IPTV Manager object"""
        self.port = port
        self.channels = channels
        self.epgdays = epgdays
        self.epgdaysback = epgdaysback 
>>>>>>> e8ca1a7 (podpora IPTV.merge)
=======
    def __init__(self, port, channels, epgdays=3, epgdaysback=1):
        """Initialize IPTV Manager object"""
        self.port = port
        self.channels = channels
        self.epgdays = epgdays
        self.epgdaysback = epgdaysback 
>>>>>>> 4a538bf (podpora pre iptv.merge)

    def via_socket(func):
        """Send the output of the wrapped function to socket"""

        def send(self):
            """Decorator to send over a socket"""
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('127.0.0.1', self.port))
            try:
                sock.sendall(json.dumps(func(self)).encode())
            finally:
                sock.close()

        return send

    @via_socket
    def send_channels(self):
        """Return JSON-STREAMS formatted python datastructure to IPTV Manager"""
        return dict(version=1, streams=self.channels)

    @via_socket
<<<<<<< HEAD
<<<<<<< HEAD
    def send_epg(self, days=3,days_back=1):
        """Return JSON-EPG formatted python data structure to IPTV Manager"""
        epg_data=get_sms_epg(days,days_back)
        return dict(version=1,epg=epg_data)
=======
    def send_epg(self):
        """Return JSON-EPG formatted python data structure to IPTV Manager"""
        epg_data=get_sms_epg(self.epgdays,self.epgdaysback)
        return dict(version=1, epg=epg_data)
>>>>>>> e8ca1a7 (podpora IPTV.merge)
=======
    def send_epg(self):
        """Return JSON-EPG formatted python data structure to IPTV Manager"""
        epg_data=get_sms_epg(self.epgdays,self.epgdaysback)
        return dict(version=1, epg=epg_data)
>>>>>>> 4a538bf (podpora pre iptv.merge)


__scriptid__   = 'plugin.video.markiza.sk'
__scriptname__ = 'markiza.sk'
__addon__      = xbmcaddon.Addon(id=__scriptid__)
__language__   = __addon__.getLocalizedString

#import web_pdb; web_pdb.set_trace()
settings = {'downloads':__addon__.getSetting('downloads'),'quality':__addon__.getSetting('quality'),'epgdays':__addon__.getSetting('epgdays')}


provider = markiza.markizaContentProvider()

if len (sys.argv)>1 and 'port' in sys.argv[2][1:]:
    channels=[]
    if 'iptv/channels' in sys.argv[0]: 
        paramstring=sys.argv[2][1:]
        params = dict(parse_qsl(paramstring))
        port=int(params['port'])

        result=provider.categories()
        for item in result:
            if item['type']!='video':
<<<<<<< HEAD
<<<<<<< HEAD
                continue					
=======
                continue
>>>>>>> e8ca1a7 (podpora IPTV.merge)
=======
                continue
>>>>>>> 4a538bf (podpora pre iptv.merge)
            item2=provider.resolve(item)
            item['url']=item2[0]['url']
            channels.append(dict(id=item['title'],name=item['title'],logo=item['img'],stream=item2[0]['url']))
        
        IPTVManager(port,channels).send_channels()
        
    if 'iptv/epg' in sys.argv[0]: 
        paramstring=sys.argv[2][1:]
        params = dict(parse_qsl(paramstring))
        port=int(params['port'])
<<<<<<< HEAD
<<<<<<< HEAD
        
        IPTVManager(port,channels).send_epg(days=int(settings['epgdays']))        
=======
        epgdays=int(settings['epgdays'])
        IPTVManager(port,channels,epgdays).send_epg()        
>>>>>>> e8ca1a7 (podpora IPTV.merge)
=======
        epgdays=int(settings['epgdays'])
        IPTVManager(port,channels,epgdays).send_epg()        
>>>>>>> 4a538bf (podpora pre iptv.merge)

else:    
    params = util.params()
    class XBMCMarkizaContentProvider(xbmcprovider.XBMCMultiResolverContentProvider):
        def render_default(self, item):
            self.render_dir(item)
            
        
    XBMCMarkizaContentProvider(provider,settings,__addon__).run(params)
