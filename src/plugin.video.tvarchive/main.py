# coding: utf-8

import sys
import urlparse
import urllib
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs
import watchlog
import os
import util


_baseUrl = sys.argv[0]
_handleId = int(sys.argv[1])
_params = dict(urlparse.parse_qsl(sys.argv[2][1:]))	
_addon = xbmcaddon.Addon()
_path = _addon.getAddonInfo('path')
	
_playlistFile = _addon.getSetting('playlistFile')
_iconsFolder = _addon.getSetting('iconsFolder')
_watchlogPath = _addon.getSetting('watchlogFolder') +  '/watchlog.db'

_episodesRefreshFlag = _path + '/refreshEpisodes'

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

	
def handlerWatched():	
	if _params['watched'] == 'true':
		watchlog.setWatched(_watchlogPath, _baseUrl, _params['item'])
	else:
		watchlog.setUnWatched(_watchlogPath,_baseUrl, _params['item'])
	with open(_episodesRefreshFlag,'w') as f:
		f.write("1") 
	xbmc.executebuiltin("Container.Refresh()")

	
	
def handlerListEpisodes():	
	xbmcplugin.setContent(_handleId, 'movies')
	watchlog.init(_watchlogPath,_path + '/watchlog.db')
	if os.path.isfile(_episodesRefreshFlag):
		os.remove(_episodesRefreshFlag)
		episodes = util.fileToObj(_path + '/' + 'content')
	else:
		handler = getattr(__import__(_params['archive']), 'getEpisodes' )	
		episodes = handler(_params['urlProgram'])
		util.objToFile(episodes, _path + '/' + 'content')
	for episode in episodes:
		infoLabels = {}
		contextMenuItems = []
		if watchlog.isWatched(_watchlogPath, _baseUrl, episode['name']):
			infoLabels['playcount'] = 1
			contextCmd = 'RunPlugin(' + _baseUrl+'?' + urllib.urlencode({'handler': 'Watched', 'item': episode['name'], 'watched': 'false'}) + ')'
			contextMenuItems.append(('UnWatched',contextCmd))
		else:
			infoLabels['playcount'] = 0
			contextCmd = 'RunPlugin(' + _baseUrl+'?' + urllib.urlencode({'handler': 'Watched', 'item': episode['name'], 'watched': 'true'}) + ')'
			contextMenuItems.append(('Watched',contextCmd))
		item = xbmcgui.ListItem(episode['name'])	
		item.setArt({'thumb': episode["thumb"], 'poster': episode["thumb"], 'fanart': episode["thumb"]})
		if 'duration' in episode.keys():
			infoLabels['duration'] = float(episode['duration'])
		if 'description' in episode.keys():
			infoLabels['plot'] = episode['description']
		item.setProperty("IsPlayable","true")
		item.setInfo( type="Video", infoLabels=infoLabels )	
		item.addContextMenuItems(contextMenuItems, replaceItems=True)	
		params = {
			'handler': 'PlayEpisode',
			'archive': _params['archive'],
			'url': episode['url'],
			'name': episode['name']
		}
		url = _baseUrl+'?' + urllib.urlencode(params)								
		xbmcplugin.addDirectoryItem(handle=_handleId, url=url, isFolder=True, listitem=item)
		
	xbmcplugin.endOfDirectory(_handleId)
	
	
def handlerPlayEpisode():		
	handler = getattr(__import__(_params['archive']), 'getStream' )	
	stream = handler(_params['url'])
	with open(_episodesRefreshFlag,'w') as f:
		f.write("1") 
	watchlog.setWatched(_watchlogPath, _baseUrl, _params['name'])
	util.play(stream, _params['name'])
	if os.path.isfile(_episodesRefreshFlag):
		xbmc.executebuiltin("Container.Refresh()")

	
def listChannels(channels):
#	xbmcplugin.setContent(_handleId, 'movies')
	for channel in channels:	
		if 'archive' not in channel.keys():
			continue
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

	
def handlerRoot():
	channels = util.m3uChannels(_playlistFile)
	listChannels(channels)	

	
if 'handler' in _params.keys():
	globals()['handler' + _params['handler']]()
else:
	handlerRoot()
	
