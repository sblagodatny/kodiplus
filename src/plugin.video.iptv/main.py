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
_playlistFile = _addon.getSetting('playlistFile')
_iconsFolder = _addon.getSetting('iconsFolder')
	
	
	
	
def listChannels(channels):
	xbmcplugin.setContent(_handleId, 'movies')
	for channel in channels:
		infoLabels = {
			'plot': ''
		}
		item = xbmcgui.ListItem(channel['name'])
		item.setProperty("IsPlayable","true")
		logo = _iconsFolder + channel['tvg_logo']
		item.setArt({'thumb': logo, 'poster': logo, 'fanart': logo})
		item.setInfo( type="Video", infoLabels=infoLabels )	
		xbmcplugin.addDirectoryItem(handle=_handleId, url=channel['url'], isFolder=False, listitem=item)
	xbmcplugin.endOfDirectory(_handleId)

	
def getChannels():	
	channels = []
	f = xbmcvfs.File (_playlistFile, 'r')
	data = f.read().splitlines()
	for i in range(0, len(data)):
		if data[i].startswith('#EXTINF'):
			try:
				channels.append({
					'tvg_id': data[i].split('tvg-id="')[1].split('"')[0],
					'name': data[i].split(',')[1],
					'tvg_logo': data[i].split('tvg-logo="')[1].split('"')[0],
					'url': data[i+1]
				})
			except:
				None
	f.close()
	return channels

	
def handlerRoot():
	reload(sys)
	sys.setdefaultencoding("utf-8")	
	listChannels(getChannels())
	

if len(_playlistFile) == 0 or len(_iconsFolder) == 0:
	xbmcgui.Dialog().ok('Error', 'Please configure settings')
else:	
	if 'handler' in _params.keys():
		globals()['handler' + _params['handler']]()
	else:
		handlerRoot()