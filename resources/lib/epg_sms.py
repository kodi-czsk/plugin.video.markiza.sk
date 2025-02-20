# -*- coding: utf-8 -*-

#v2.25.1

import sys
import xbmc
import os
import xml.etree.ElementTree as ET
import unicodedata
import time
import time
import json
import urllib.request, urllib.parse, urllib.error
import datetime
TV_SMS_CZ_IDS = "8,225,683,15402,15568"#markiza,doma,dajto,krimi,klasik
file_name = "epg.xml"
update = 0

def fetchUrl(url, headers, opener=None, ref=None):
	httpdata = ''	           
	req = urllib.request.Request(url)
	req.add_header('User-Agent', headers['user-agent'])
	if ref:
	    req.add_header('Referer', ref)
	if opener:
	    resp = opener.open(req)
	else:
	    resp = urllib.request.urlopen(req)
	httpdata = resp.read().decode('utf-8')
	resp.close()
	return httpdata

now = datetime.datetime.now()
local_now = now.astimezone()
TS = " " + str(local_now)[-6:].replace(":", "")
tz=local_now.tzinfo
if 'Daylight' in str(tz):
    timezone='+0200'
    print('DAYLIGHT',timezone)
else:
    timezone='+0100'
    print('NO DAYLIGHT',timezone)

def encode(string):
    string = str(unicodedata.normalize('NFKD', string).encode('ascii', 'ignore'), "utf-8")
    return string


custom_names = []
try:
    f = open(custom_names_path, "r", encoding="utf-8").read().splitlines()
    for x in f:
        x = x.split("=")
        custom_names.append((x[0], x[1]))
except:
    pass


def replace_names(value):
    for v in custom_names:
        if v[0] == value:
            value = v[1]
    return value




class Get_channels_sms:

    def __init__(self):
        self.channels = []
        headers = {"user-agent": "SMSTVP/1.7.3 (242;cs_CZ) ID/ef284441-c1cd-4f9e-8e30-f5d8b1ac170c HW/Redmi Note 7 Android/10 (QKQ1.190910.002)"}
        #self.html = requests.get("http://programandroid.365dni.cz/android/v6-tv.php?locale=cs_CZ", headers = headers).text
        self.html = fetchUrl("http://programandroid.365dni.cz/android/v6-tv.php?locale=cs_CZ",headers)
        self.ch = {}

    def all_channels(self):
        try:
            root = ET.fromstring(self.html)
            for i in root.iter("a"):
                self.ch[i.attrib["id"]] = encode((i.attrib["id"] + "-" + i.find("n").text).replace(" ", "-").lower())
                try:
                    icon = "http://sms.cz/kategorie/televize/bmp/loga/velka/" + i.find("o").text
                except:
                    icon = ""
                self.channels.append({"display-name": [(replace_names(i.find("n").text), u"cs")], "id": encode((i.attrib["id"] + "-" + i.find("n").text).replace(" ", "-").lower()), "icon": [{"src": icon}]})
            self.f.close()
        except:
            pass
        return self.ch, self.channels

    def cz_sk_channels(self):
        try:
            root = ET.fromstring(self.html)
            for i in root.iter("a"):
                if i.find("p").text == "České" or i.find("p").text == "Slovenské":
                    self.ch[i.attrib["id"]] = encode((i.attrib["id"] + "-" + i.find("n").text).replace(" ", "-").lower())
                    try:
                        icon = "http://sms.cz/kategorie/televize/bmp/loga/velka/" + i.find("o").text
                    except:
                        icon = ""
                    self.channels.append({"display-name": [(replace_names(i.find("n").text), u"cs")], "id": encode((i.attrib["id"] + "-" + i.find("n").text).replace(" ", "-").lower()), "icon": [{"src": icon}]})
        except:
            pass
        return self.ch, self.channels

    def own_channels(self, cchc):
        try:
            root = ET.fromstring(self.html)
            cchc = cchc.split(",")
            for i in root.iter("a"):
                if i.attrib["id"] in cchc:
                    self.ch[i.attrib["id"]] = encode((i.attrib["id"] + "-" + i.find("n").text).replace(" ", "-").lower())
                    try:
                        icon = "http://sms.cz/kategorie/televize/bmp/loga/velka/" + i.find("o").text
                    except:
                        icon = ""
                    self.channels.append({"display-name": [(replace_names(i.find("n").text), u"cs")], "id": encode((i.attrib["id"] + "-" + i.find("n").text).replace(" ", "-").lower()), "icon": [{"src": icon}]})
        except:
            pass
        return self.ch, self.channels


class Get_programmes_sms:

    def __init__(self, days_back, days):
        self.programmes_sms = []
        self.days_back = days_back
        self.days = days

    def data_programmes(self, ch):
        if ch != {}:
            chl = ",".join(ch.keys())
            now = datetime.datetime.now()
            for i in range(self.days_back*-1, self.days):
                next_day = now + datetime.timedelta(days = i)
                date = next_day.strftime("%Y-%m-%d")
                date_ = next_day.strftime("%d.%m.%Y")
                headers = {"user-agent": "SMSTVP/1.7.3 (242;cs_CZ) ID/ef284441-c1cd-4f9e-8e30-f5d8b1ac170c HW/Redmi Note 7 Android/10 (QKQ1.190910.002)"}
                print(date_)
                html = fetchUrl("http://programandroid.365dni.cz/android/v6-program.php?datum=" + date + "&id_tv=" + chl, headers = headers)
                root = ET.fromstring(html)
                root[:] = sorted(root, key=lambda child: (child.tag,child.get("o")))
                for i in root.iter("p"):
                    n = i.find("n").text
                    try:
                        k = i.find("k").text
                    except:
                        k = ""
                    if i.attrib["id_tv"] in ch:
                        self.programmes_sms.append({"channel": ch[i.attrib["id_tv"]].replace("804-ct-art", "805-ct-:d"), "start": i.attrib["o"].replace("-", "").replace(":", "").replace(" ", "") + TS, "stop": i.attrib["d"].replace("-", "").replace(":", "").replace(" ", "") + TS, "title": [(n, "")], "desc": [(k, "")]})
                sys.stdout.write('\x1b[1A')
                print(date_ + "  OK")
        print("\n")
        return self.programmes_sms


def get_sms_epg(days=3,days_back=1):
    global timezone
    channels = []
    programmes = []
    #try:
    if True:
        print("TV.SMS.cz kanály")
        print("Stahuji data...")
        g = Get_channels_sms()
        if TV_SMS_CZ_IDS == "":
            ch, channels_sms = g.all_channels()
        else:
            ch, channels_sms = g.own_channels(TV_SMS_CZ_IDS)
        channels.extend(channels_sms)
        gg = Get_programmes_sms(days_back, days)
        programmes_sms = gg.data_programmes(ch)
        programmes.extend(programmes_sms)
    #except Exception as ex:
    #    print("Chyba\n")
    #    print("TV.SMS.cz kanály - %s" % ex)
    #    #logging.error("TV.SMS.cz kanály - %s" % ex)

    if channels != []:
        print("Celkem kanálů: " + str(len(channels)))
        print("Generuji...")
        json_programs={}
        try:
            for c in channels:
                print(c)
                
            #timezone = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Settings.GetSettingValue", "params": {"setting": "locale.timezone"}, "id": 1}')            
            for p in programmes:
                #print(p)
                #print(p['title'])
                #print(p['title'][0])
                #print(p['title'][0][0])
                #print(type(p['title']))
                #exit(0)
                channel=p['channel']
                if channel=='225-doma':
                    channel='Live Doma'
                if channel=='683-tv-dajto':
                    channel='Live Dajto'
                if channel=='8-markiza':
                    channel='Live Markiza'
                if channel=='15402-markiza-krimi':
                    channel='Live Krimi'
                if channel=='15568-markiza-klasik':
                    channel='Live Klasik'					
                if not channel in json_programs:
                    json_programs[channel]=[]
                #"start": "20240401055500 +0200",
                #"start": "2020-04-01T12:45:00"
				
				
                a=p['start']
                time_start= a[0:4]+'-'+a[4:6]+'-'+a[6:8]+'T'+a[8:10]+':'+a[10:12]+':'+a[12:14] + '.000'+timezone#Treba doriesit zistenie ci je DST Daylight saving time
                a=p['stop']
                time_stop = a[0:4]+'-'+a[4:6]+'-'+a[6:8]+'T'+a[8:10]+':'+a[10:12]+':'+a[12:14] + '.000'+timezone#Treba doriesit zistenie ci je DST Daylight saving time
                program={'title':p['title'][0][0],'start':time_start,'stop':time_stop,'description':p['desc'][0][0]}
                json_programs[channel].append(program)

            sys.stdout.write('\x1b[1A')
            sys.stdout.write('\x1b[2K')
            now = datetime.datetime.now()
            dt = now.strftime("%d.%m.%Y %H:%M")
            
            json_data={}
            for c in json_programs:
                json_data[c]=json_programs[c]
            return(json_data)

        except Exception as ex:
            return({})

    return({})        

if __name__ == "__main__":
    print(get_sms_epg())

