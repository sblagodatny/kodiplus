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
_epgDays = int(_addon.getSetting('epgDays'))
	
	
	
	
def epgToXmltv(epgs):
	idChannel = 1
	idProgram = 1
	f = util.fopen(_epgFile, 'w')
#	f = codecs.open(_epgFile, "w", "utf-8")
	f.write('<?xml version="1.0" encoding="utf-8"?>' + "\n")
	f.write('<!DOCTYPE tv SYSTEM "http://www.teleguide.info/download/xmltv.dtd">' + "\n")
	f.write('<tv generator-info-name="TVH_W/0.751l" generator-info-url="http://www.teleguide.info/">' + "\n")
	for epg in epgs:
		for channel in epg.keys():
			f.write('<channel id="' + str(idChannel) + '" ><display-name>' + channel.encode('utf-8') + '</display-name></channel>' + "\n")
			for i in range (0, len(epg[channel])-1):
				program = epg[channel][i]
				start = datetime.datetime.strftime(program['time'],'%Y%m%d%H%M%S')
				nextprogram = epg[channel][i+1]				
				stop = datetime.datetime.strftime(nextprogram['time'],'%Y%m%d%H%M%S')
				f.write('<programme id="' + str(idProgram) + '" start="' + start + '" stop="' + stop + '" channel="' + str(idChannel) + '" >' + "\n")
				f.write('<title>' + program['name'].encode('utf-8') + '</title>' + "\n")
				if 'description' in program.keys():
					f.write('<desc>' + program['description'].encode('utf-8') + '</desc>' + "\n")
				f.write('</programme>' + "\n")
				idProgram = idProgram + 1
			idChannel = idChannel + 1					
	f.write('</tv>' + "\n")
	f.close()


def m3uToList(plfile):	
	result = []
#	f = codecs.open(plfile, "r", "utf-8")
	f = util.fopen(plfile, 'r')
	for line in f.read().splitlines():
		if line.startswith('#EXTINF'):
			result.append(line.split(',')[1].lstrip().rstrip())
	f.close()
	return result
		

def getTagValue(f, tag, endtag, currentline):	
	line = currentline
	while '</' + endtag + '>' not in line:
		if '<' + tag in line:
			return line.split('<' + tag)[1].split('>')[1].split('<')[0]
		line = f.readline()	
	return ''

	
def xmltvToEpg2(url, channelNames, days, timeshift):
	import zlib
	tmp = _path + '/stas.xml'
	response = requests.get(url)
	data = zlib.decompress(response.content, zlib.MAX_WBITS|32)
	with open(tmp, 'w') as f:
		f.write(data)
	programs = {}
	channels = {}
	tsstart = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())
	tsend = tsstart + datetime.timedelta(days=days)
	with codecs.open(tmp, "r", "utf-8") as f:
		line = f.readline()
		while line:
			if line.startswith('<channel'):
				id = line.split('id="')[1].split('"')[0]
				name = getTagValue(f, 'display-name', 'channel', line)
				if name in channelNames:			
					programs[id] = []
					channels[name] = id			
			if line.startswith('<programme'):
				idChannel = line.split('channel="')[1].split('"')[0]
				ts = line.split('start="')[1].split('"')[0].split(' ')[0]					
				ts = datetime.datetime(int(ts[0:4]),int(ts[4:6]),int(ts[6:8]),int(ts[8:10]),int(ts[10:12]))
				ts = ts + datetime.timedelta(hours=timeshift)
				name = getTagValue(f, 'title', 'programme', line)				
				desc = getTagValue(f, 'desc', 'programme', line)						
				if idChannel in programs.keys() and ts > tsstart and ts < tsend:				
					programs[idChannel].append({'time': ts, 'name': name, 'description': desc})			
			line = f.readline()
	os.remove(tmp)
	result = {}
	for channel in channels.keys():
		result[channel] = programs[channels[channel]]
	return result	
	
	

	
	
def handlerRoot():
	reload(sys)
	sys.setdefaultencoding("utf-8")
	channels = m3uToList(_playlistFile)
	epgToXmltv([
		xmltvToEpg2('http://api.torrent-tv.ru/ttv.xmltv.xml.gz', channels, _epgDays, -1),
		epgIsrael.getEPG(_epgDays, channels)
	])
	
	
	
if 'handler' in _params.keys():
	globals()['handler' + _params['handler']]()
else:
	handlerRoot()
	
