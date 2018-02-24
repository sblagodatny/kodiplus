# coding: utf-8

import sys
import urlparse
import urllib
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs



_baseUrl = sys.argv[0]
_handleId = int(sys.argv[1])
_params = dict(urlparse.parse_qsl(sys.argv[2][1:]))	
_addon = xbmcaddon.Addon()
_path = _addon.getAddonInfo('path')
	
_playlistFile = _addon.getSetting('playlistFile')
_iconsFolder = _addon.getSetting('iconsFolder')

reload(sys)
sys.setdefaultencoding("utf-8")	


def handlerListCategories():
	params = {
		'handler': 'ListPrograms',
		'archive': _params['archive']
	}
	handler = getattr(__import__(_params['archive']), 'getCategories' )
	if 'archiveParams' in _params.keys():
		categories = handler(_params['archiveParams'])
	else:
		categories = handler()	
	for category in categories:																		
		item = xbmcgui.ListItem(category['name'])
		params.update({'urlCategory': category['url']}) 
		xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?' + urllib.urlencode(params), isFolder=True, listitem=item)
	xbmcplugin.endOfDirectory(_handleId)
	
	
def handlerListPrograms():
	xbmcplugin.setContent(_handleId, 'movies')
	handler = getattr(__import__(_params['archive']), 'getPrograms' )	
	programs = handler(_params['urlCategory'])
	for program in programs:			
		item = xbmcgui.ListItem(program['name'])
		item.setArt({'thumb': program["thumb"], 'poster': program["thumb"], 'fanart': program["thumb"]})
		item.setProperty("IsPlayable","false")	
		infoLabels = {'plot': program['description']}	
		item.setInfo( type="Video", infoLabels=infoLabels )		
		params = {
			'handler': 'ListEpisodes',
			'archive': _params['archive'],
			'urlProgram': program['url']
		}						
		xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?' + urllib.urlencode(params), isFolder=True, listitem=item)
	xbmcplugin.endOfDirectory(_handleId)

	
def handlerListEpisodes():
	xbmcplugin.setContent(_handleId, 'movies')
	handler = getattr(__import__(_params['archive']), 'getEpisodes' )	
	episodes = handler(_params['urlProgram'])
	for episode in episodes:
		item = xbmcgui.ListItem(episode['name'])
		item.setArt({'thumb': episode["thumb"], 'poster': episode["thumb"], 'fanart': episode["thumb"]})
		infoLabels = {}
		if 'duration' in episode.keys():
			infoLabels['duration'] = float(episode['duration'])
		if 'description' in episode.keys():
			infoLabels['plot'] = episode['description']
		item.setProperty("IsPlayable","true")
		item.setInfo( type="Video", infoLabels=infoLabels )	
		params = {
			'handler': 'PlayEpisode',
			'archive': _params['archive'],
			'urlEpisode': episode['url']
		}
		url = _baseUrl+'?' + urllib.urlencode(params)						
		xbmcplugin.addDirectoryItem(handle=_handleId, url=url, isFolder=False, listitem=item)
	xbmcplugin.endOfDirectory(_handleId)
	
	
def handlerPlayEpisode():		
	handler = getattr(__import__(_params['archive']), 'getStream' )	
	stream = handler(_params['urlEpisode'])
	item=xbmcgui.ListItem()
	item.setPath(stream)
	xbmcplugin.setResolvedUrl(_handleId, True, listitem=item)		
	


def listChannels(channels):
#	xbmcplugin.setContent(_handleId, 'movies')
	for channel in channels:																		
		item = xbmcgui.ListItem(channel['name'])
		if 'tvg_logo' in channel.keys():
			logo = _iconsFolder + channel['tvg_logo']
			item.setArt({'thumb': logo, 'poster': logo, 'fanart': logo})
		
		archive = channel['archive']
		archiveParams = None
		if '|' in archive:
			archiveParams = archive.split('|')[1]
			archive = archive.split('|')[0]
		params = {
			'handler': 'ListCategories',
			'archive': archive
		}	
		if archiveParams is not None:
			params.update({'archiveParams': archiveParams})
		xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?' + urllib.urlencode(params), isFolder=True, listitem=item)
	xbmcplugin.endOfDirectory(_handleId)

	
def getChannels():	
	channels = []
	f = xbmcvfs.File (_playlistFile, 'r')
	data = f.read().splitlines()
	for i in range(0, len(data)):
		if data[i].startswith('#EXTINF'):
			channel = {
				'name': data[i].split(',')[1],
			}			
			try:
				channel.update({'archive': data[i].split('archive="')[1].split('"')[0]})
			except:
				continue			
			try:				
				channel.update({'tvg_logo': data[i].split('tvg-logo="')[1].split('"')[0]})
			except:
				None			
			channels.append(channel)
			
	f.close()
	return channels

	
def handlerRoot():
	listChannels(getChannels())	

	
if 'handler' in _params.keys():
	globals()['handler' + _params['handler']]()
else:
	handlerRoot()
	
