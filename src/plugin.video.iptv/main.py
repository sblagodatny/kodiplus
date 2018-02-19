# coding: utf-8

import sys
import urlparse
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs
import datetime
import util
import urllib
from bs4 import BeautifulSoup




_baseUrl = sys.argv[0]
_handleId = int(sys.argv[1])
_params = dict(urlparse.parse_qsl(sys.argv[2][1:]))	
_addon = xbmcaddon.Addon()
_path = _addon.getAddonInfo('icon').replace('icon.png','')
	
_epgFile = _addon.getSetting('epgFile')
_playlistFile = _addon.getSetting('playlistFile')
_iconsFolder = _addon.getSetting('iconsFolder')
	
	
	
	
def listChannels(channels, epg):
	xbmcplugin.setContent(_handleId, 'movies')
	for channel in channels:
		infoLabels = {}	
		if 'tvg_id' in channel.keys():
			try:
				epgc = epg[channel['tvg_id']]
				infoLabels = {'plot': util.bold(epgc['title']) + "\n\n" + 'Осталось: ' + str(int(epgc['remaining']/60)) + " минут" + "\n\n" + epgc['description']}
			except:
				None			
		contextMenuItems = []
		contextCmd = 'Container.Refresh()'
		contextMenuItems.append(('Refresh',contextCmd))															
		item = xbmcgui.ListItem(channel['name'])
		item.addContextMenuItems(contextMenuItems, replaceItems=True)
		if 'tvg_logo' in channel.keys():
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
			channel = {
				'name': data[i].split(',')[1],
				'url': data[i+1]
			}
			try:
				channel.update({'tvg_id': data[i].split('tvg-id="')[1].split('"')[0]})
			except:
				None
			try:				
				channel.update({'tvg_logo': data[i].split('tvg-logo="')[1].split('"')[0]})
			except:
				None
			channels.append(channel)
	f.close()
	return channels

	
def getEPG():
	try:
		epg = {}
		f = xbmcvfs.File (_epgFile, 'r')
		data = f.read()
		f.close()
		data = BeautifulSoup(data, "html.parser")
		now = util.now()
		for program in data.find_all('programme'):
			start = util.strToDateTime(program['start'])
			stop = util.strToDateTime(program['stop'])
			if now >= start and now < stop:
				remaining = (stop-now).seconds
				epg.update({
					program['channel']: {'title': program.find('title').get_text(), 'description': program.find('desc').get_text(), 'remaining': remaining}
				})	
		return epg
	except:
		return None


def handlerRoot():
	reload(sys)
	sys.setdefaultencoding("utf-8")	
	listChannels(getChannels(), getEPG())
	
	
if len(_playlistFile) == 0 or len(_iconsFolder) == 0:
	xbmcgui.Dialog().ok('Error', 'Please configure settings')
else:	
	if 'handler' in _params.keys():
		globals()['handler' + _params['handler']]()
	else:
		handlerRoot()
