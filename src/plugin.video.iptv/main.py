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
				infoLabels = {'plot': util.bold(epgc['title']) + '  [' + str(epgc['remaining']) + "] \n\n" + epgc['description']}
			except:
				None			
		contextMenuItems = []
		contextCmd = 'Container.Refresh()'
		contextMenuItems.append(('Refresh',contextCmd))
		if 'archive' in channel.keys():
			archive = channel['archive']
			archiveParams = None
			if '|' in archive:
				archiveParams = archive.split('|')[1]
				archive = archive.split('|')[0]
			params = {
				'handle': _handleId,
				'handler': 'ListCategories',
				'archive': archive
			}	
			if archiveParams is not None:
				params.update({'archiveParams': archiveParams})
			archiveAddonUrl = 'plugin://plugin.video.tvarchive/'
			contextCmd = 'ActivateWindow(Videos,' + archiveAddonUrl + '?' + urllib.urlencode(params) + ',return)'
			contextMenuItems.append(('Arhive',contextCmd))
		item = xbmcgui.ListItem(channel['name'])
		item.addContextMenuItems(contextMenuItems, replaceItems=True)
		if 'tvg_logo' in channel.keys():
			logo = _iconsFolder + channel['tvg_logo']
			item.setArt({'thumb': logo, 'poster': logo, 'fanart': logo})
		item.setInfo( type="Video", infoLabels=infoLabels )
		params = {
			'handler': 'Play',
			'name': channel['name'],
			'url': channel['url']
		}
		url = _baseUrl+'?' + urllib.urlencode(params)
		xbmcplugin.addDirectoryItem(handle=_handleId, url=url, isFolder=True, listitem=item)
	xbmcplugin.endOfDirectory(_handleId)
	
	
def handlerPlay():		
	item=xbmcgui.ListItem(_params['name'])
	item.setPath(_params['url'])
	xbmc.Player().play(_params['url'],item)


def handlerRoot():
	channels = util.m3uChannels(_playlistFile)
	epg = util.xmltvCurrentPrograms(channels, _epgFile)
	listChannels(channels, epg)
	
	
if len(_playlistFile) == 0 or len(_iconsFolder) == 0:
	xbmcgui.Dialog().ok('Error', 'Please configure settings')
else:	
	if 'handler' in _params.keys():
		globals()['handler' + _params['handler']]()
	else:
		handlerRoot()
