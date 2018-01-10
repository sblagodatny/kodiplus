# coding: utf-8

import sys
import urlparse
import urllib
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

import vodTNT


_baseUrl = sys.argv[0]
_handleId = int(sys.argv[1])
_params = dict(urlparse.parse_qsl(sys.argv[2][1:]))	
_addon = xbmcaddon.Addon()
_path = _addon.getAddonInfo('path')
	

reload(sys)  
sys.setdefaultencoding('utf8')	

	
def handlerListPrograms():
#	xbmcplugin.setContent(_handleId, 'movies')
	programs = vodTNT.getPrograms()
	for program in programs:			
		item = xbmcgui.ListItem(program['name'], iconImage=program["thumb"] )
		item.setProperty("IsPlayable","false")	
		params = {
			'handler': 'ListEpisodes',
			'urlProgram': program['url']
		}						
		xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?' + urllib.urlencode(params), isFolder=True, listitem=item)
	xbmcplugin.endOfDirectory(_handleId)

	
def handlerListSeasons():
	seasons = vodTNT.getSeasons(_params['urlProgram'])
	for season in seasons:			
		item = xbmcgui.ListItem(season['name'], iconImage=season["thumb"] )
		item.setProperty("IsPlayable","false")	
		params = {
			'handler': 'ListEpisodes',
			'urlSeason': season['url']
		}						
		xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?' + urllib.urlencode(params), isFolder=True, listitem=item)
	xbmcplugin.endOfDirectory(_handleId)
	
	
def handlerListEpisodes():
#	xbmcplugin.setContent(_handleId, 'movies')
	episodes = vodTNT.getEpisodes(_params['urlProgram'])
	for episode in episodes:			
		item = xbmcgui.ListItem(episode['name'], iconImage=episode["thumb"] )
		item.setProperty("IsPlayable","true")	
		params = {
			'handler': 'PlayEpisode',
			'urlEpisode': episode['url']
		}						
		xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?' + urllib.urlencode(params), isFolder=False, listitem=item)
	xbmcplugin.endOfDirectory(_handleId)
	
	
def handlerPlayEpisode():	
	url = vodTNT.getStream(_params['urlEpisode'])
#	xbmcgui.Dialog().ok('Notice', url)
	item=xbmcgui.ListItem()
	item.setPath(url)
	xbmcplugin.setResolvedUrl(_handleId, True, listitem=item)		
	return		


	
def handlerRoot():
	
	### Build base list ###
	pathImg = _path + '/resources/img/'
	xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?' + urllib.urlencode({'handler': 'ListPrograms'}), isFolder=True, listitem=xbmcgui.ListItem('ТНТ', iconImage=pathImg+'TNT.png'))
	xbmcplugin.endOfDirectory(_handleId)

	
if 'handler' in _params.keys():
	globals()['handler' + _params['handler']]()
else:
	handlerRoot()
	
