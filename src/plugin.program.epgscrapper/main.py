# coding: utf-8

import sys
import urlparse
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs
#import util
import datetime



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
	
	

	
def handlerRoot():
	reload(sys)
	sys.setdefaultencoding("utf-8")	
	
	channels = []
	f = xbmcvfs.File (_playlistFile, 'r')
	for line in f.read().splitlines():
		if line.startswith('#EXTINF'):
			try:
				channels.append({
					'id': line.split('tvg-id="')[1].split('"')[0],
					'name': line.split(',')[1]
				})
			except:
				None
	f.close()
	
	pid = 1
	f = xbmcvfs.File (_epgFile, 'w')
	f.write('<?xml version="1.0" encoding="utf-8"?>' + "\n")
	f.write('<!DOCTYPE tv SYSTEM "http://xmltv.cvs.sourceforge.net/viewvc/xmltv/xmltv/xmltv.dtd">' + "\n")
	f.write('<tv>' + "\n")
	for channel in channels:
			xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(_addon.getAddonInfo('name'),channel['name'], 1, _addon.getAddonInfo('icon')))
			f.write('<channel id="' + channel['id'] + '" ><display-name>' + channel['name'].encode('utf-8') + '</display-name></channel>' + "\n")
			scrapper = getattr(__import__('scrappers'), 'getEpg' + channel['id'].split('_')[0])			
			programs = scrapper(channel['id'].split('_')[1], _epgDays)
			for program in programs:
				start = datetime.datetime.strftime(program['start'],'%Y%m%d%H%M%S %z')
				stop = datetime.datetime.strftime(program['stop'],'%Y%m%d%H%M%S %z')
				f.write('<programme id="' + str(pid) + '" start="' + start + '" stop="' + stop + '" channel="' + channel['id'] + '" >' + "\n")
				f.write('<title>' + program['title'].encode('utf-8') + '</title>' + "\n")
				f.write('<desc>' + program['description'].encode('utf-8') + '</desc>' + "\n")
				f.write('</programme>' + "\n")
				pid = pid + 1			
	f.write('</tv>' + "\n")
	f.close()
	
	

	
	
	
if 'handler' in _params.keys():
	globals()['handler' + _params['handler']]()
else:
	handlerRoot()
