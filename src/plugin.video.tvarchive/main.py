# coding: utf-8

import sys
import urlparse
import urllib
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

#import vodTNT
#import vod1TV


_baseUrl = sys.argv[0]
_handleId = int(sys.argv[1])
_params = dict(urlparse.parse_qsl(sys.argv[2][1:]))	
_addon = xbmcaddon.Addon()
_path = _addon.getAddonInfo('path')
	

reload(sys)  
sys.setdefaultencoding('utf8')	

	
def handlerListPrograms():
#	xbmcplugin.setContent(_handleId, 'movies')
	handler = getattr(__import__(_params['arhiveHandler']), 'getPrograms' )	
	programs = handler()
	for program in programs:			
		item = xbmcgui.ListItem(program['name'], iconImage=program["thumb"] )
		item.setProperty("IsPlayable","false")	
		params = {
			'handler': 'ListEpisodes',
			'arhiveHandler': _params['arhiveHandler'],
			'urlProgram': program['url']
		}						
		xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?' + urllib.urlencode(params), isFolder=True, listitem=item)
	xbmcplugin.endOfDirectory(_handleId)
	
	
def handlerListEpisodes():
#	xbmcplugin.setContent(_handleId, 'movies')
	handler = getattr(__import__(_params['arhiveHandler']), 'getEpisodes' )	
	episodes = handler(_params['urlProgram'])
	for episode in episodes:			
		item = xbmcgui.ListItem(episode['name'], iconImage=episode["thumb"] )
		item.setProperty("IsPlayable","true")	
		if 'streams' in episode.keys():
			url = episode['streams'][-1]
		else:
			params = {
				'handler': 'PlayEpisode',
				'arhiveHandler': _params['arhiveHandler'],
				'urlEpisode': episode['url']
			}
			url = _baseUrl+'?' + urllib.urlencode(params)
								
		xbmcplugin.addDirectoryItem(handle=_handleId, url=url, isFolder=False, listitem=item)
	xbmcplugin.endOfDirectory(_handleId)
	
	
def handlerPlayEpisode():	
	handler = getattr(__import__(_params['arhiveHandler']), 'getStreams' )	
	streams = handler(_params['urlEpisode'])
#	xbmcgui.Dialog().ok('Notice', url)
	item=xbmcgui.ListItem()
	item.setPath(streams[-1])
	xbmcplugin.setResolvedUrl(_handleId, True, listitem=item)		
	return		


	
def handlerRoot():
	
	### Build base list ###
	channels = [
		{'arhiveHandler': 'handlerTNT', 'name': 'ТНТ', 'thumb': 'TNT.png'},
		{'arhiveHandler': 'handler1TV', 'name': 'Первый', 'thumb': '1TV.png'}
	]
	
	pathImg = _path + '/resources/img/'
	for channel in channels:
		params = {
			'handler': 'ListPrograms',
			'arhiveHandler': channel['arhiveHandler']
		}
		item = xbmcgui.ListItem(channel['name'], iconImage=pathImg + channel['thumb'])
		xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?' + urllib.urlencode(params), isFolder=True, listitem=item)
	xbmcplugin.endOfDirectory(_handleId)

	
if 'handler' in _params.keys():
	globals()['handler' + _params['handler']]()
else:
	handlerRoot()
	
