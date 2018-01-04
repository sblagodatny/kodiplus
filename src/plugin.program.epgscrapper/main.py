# coding: utf-8

import sys
import urlparse
import xbmc
import xbmcgui
import xbmcplugin
import xbmcvfs
import urllib
import xbmcaddon
import util
import os
import datetime
import epgIsrael
from bs4 import BeautifulSoup
import io
import datetime
import time
import codecs
import requests



_baseUrl = sys.argv[0]
_handleId = int(sys.argv[1])
_params = dict(urlparse.parse_qsl(sys.argv[2][1:]))	
_addon = xbmcaddon.Addon()
_path = _addon.getAddonInfo('icon').replace('icon.png','')
	
_epgFile = _addon.getSetting('epgFile')
if len(_epgFile) == 0:
	_epgFile = _path + '/epg.xml'
_playlistFile = _addon.getSetting('playlistFile')
if len(_playlistFile) == 0:
	_playlistFile = _path + '/channels.m3u8'		
_epgDays = int(_addon.getSetting('epgDays'))+1
	
	
_xmltvUrls = ['http://api.torrent-tv.ru/ttv.xmltv.xml.gz']
	
	

	
def handlerRoot():
	reload(sys)
	sys.setdefaultencoding("utf-8")
	names = util.m3uParse(_playlistFile)
	epgs = []
	
	epg = epgIsrael.getEPG(_epgDays)
	epg = util.filterByName(epg, names)
	epgs.append(epg)
	
	tmp = _path + '/tmp'
	for url in _xmltvUrls:
		util.wgetZip(url, tmp)
		epg = util.xmltvParse(tmp)
		epg = util.filterByName(epg, names)
		epg = util.filterByDays(epg, _epgDays)
		epgs.append(epg)
	os.remove(tmp)
	
	util.xmltvWriteMultiple(epgs, _epgFile)	

	
	
	
if 'handler' in _params.keys():
	globals()['handler' + _params['handler']]()
else:
	handlerRoot()
	
