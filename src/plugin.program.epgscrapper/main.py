# coding: utf-8

import sys
import urlparse
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs
import util
import datetime



_baseUrl = sys.argv[0]
_handleId = int(sys.argv[1])
_params = dict(urlparse.parse_qsl(sys.argv[2][1:]))	
_addon = xbmcaddon.Addon()
_path = _addon.getAddonInfo('icon').replace('icon.png','')

_epgFile = _addon.getSetting('epgFile')
_playlistFile = _addon.getSetting('playlistFile')
_epgDays = int(_addon.getSetting('epgDays'))+1

reload(sys)
sys.setdefaultencoding("utf-8")	


	
def handlerRoot():
	channels = util.m3uChannels(_playlistFile)
	pid = 1
	f = xbmcvfs.File (_epgFile, 'w')
	f.write('<?xml version="1.0" encoding="utf-8"?>' + "\n")
	f.write('<!DOCTYPE tv SYSTEM "http://xmltv.cvs.sourceforge.net/viewvc/xmltv/xmltv/xmltv.dtd">' + "\n")
	f.write('<tv>' + "\n")
	for channel in channels:
			if 'tvg_id' not in channel.keys():
				continue
			xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(_addon.getAddonInfo('name'),channel['name'], 1, _addon.getAddonInfo('icon')))
			f.write('<channel id="' + channel['tvg_id'] + '" ><display-name>' + channel['name'].encode('utf-8') + '</display-name></channel>' + "\n")
			scrapper = getattr(__import__('scrappers'), 'getEpg' + channel['tvg_id'].split('_')[0])			
			for i in range (0,3):
				try:
					programs = scrapper(channel['tvg_id'].split('_')[1], _epgDays)
					break
				except:
					None
			for program in programs:
				start = program['start']
				stop = program['stop']
				sstart = datetime.datetime.strftime(start,'%Y%m%d%H%M%S %z')
				sstop = datetime.datetime.strftime(stop,'%Y%m%d%H%M%S %z')
				f.write('<programme id="' + str(pid) + '" start="' + sstart + '" stop="' + sstop + '" channel="' + channel['tvg_id'] + '" >' + "\n")
				f.write('<title>' + program['title'].encode('utf-8') + '</title>' + "\n")
				f.write('<desc>' + program['description'].encode('utf-8') + '</desc>' + "\n")
				f.write('</programme>' + "\n")
				pid = pid + 1			
	f.write('</tv>' + "\n")
	f.close()
	
	

if len(_playlistFile) == 0 or len(_epgFile) == 0:
	xbmcgui.Dialog().ok('Error', 'Please configure settings')
else:	
	if 'handler' in _params.keys():
		globals()['handler' + _params['handler']]()
	else:
		handlerRoot()
