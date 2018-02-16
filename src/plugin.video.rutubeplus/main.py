# coding: utf-8

import sys
import urlparse
import urllib
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import rutube
import youtube
import util
import google

_baseUrl = sys.argv[0]
_handleId = int(sys.argv[1])
_params = dict(urlparse.parse_qsl(sys.argv[2][1:]))	
_addon = xbmcaddon.Addon()
_path = _addon.getAddonInfo('path')

_forceLowQuality = False
if _addon.getSetting('forceLowQuality')=='true':
	_forceLowQuality = True


_googleUser=_addon.getSetting('googleUser')
_googlePassword=_addon.getSetting('googlePassword')
_cookiesFolder = _addon.getSetting('cookiesFolder')
if len(_cookiesFolder) == 0:
	_cookiesFolder = _path	

	
reload(sys)  
sys.setdefaultencoding('utf8')	


def handlerPlay():
	streams = rutube.getStreams(_params['videoId'])
	quality = '640x360'
	if _forceLowQuality:
		quality = '512x288'
	if quality in streams.keys():
		stream = streams[quality]
	else:
		stream = streams [streams.keys()[0]]		
	item=xbmcgui.ListItem()
	item.setPath(stream)
	xbmcplugin.setResolvedUrl(_handleId, True, listitem=item)	

	
def handlerPlayYouTube():
	s = util.Session(_cookiesFolder)
	google.loginVerify(s, _googleUser, _googlePassword)
	search = _params['contentName'] + ' ' + _params['season'] +' сезон ' + _params['episode'] +' серия '
	videos = youtube.searchVideos(search, s)
	if len(videos) == 0:
		xbmcgui.Dialog().ok('Error', 'Unable to get YouTube stream')
		return
	video = videos[0]
	if not xbmcgui.Dialog().ok('Notice', 'Found YouTube stream:', ' ',video['name']):
		return		
	streams = youtube.getStreams(video['id'], s)
	itag = util.firstMatch(youtube.itagsVod, streams.keys())
	if itag is None:
		xbmcgui.Dialog().ok('Error', 'Unable to get YouTube stream')
		return
	stream = streams[itag]
	item=xbmcgui.ListItem()
	item.setPath(stream)
	xbmc.Player().play(stream,item) 
	
	
def handlerContentVideos():
	videos = rutube.contentVideos(_params['contentId'], _params['season'])
	xbmcplugin.setContent(_handleId, 'movies')
	for video in videos:
		infoLabels = {
			'plot': 'Дата выпуска: ' + video['created'] + "\n \n" + video['description'],
			'duration': float(video['duration'])
		}
		contextMenuItems = []
		item = xbmcgui.ListItem(video['name'])
		item.setProperty("IsPlayable","true")
		item.setArt({'thumb': video["thumb"], 'poster': video["thumb"], 'fanart': video["thumb"]})
		item.setInfo( type="Video", infoLabels=infoLabels )	
		params = {
			'handler': 'PlayYouTube',
			'contentName': _params['contentName'],
			'season': _params['season'],
			'episode': video['episode']				
		}
		contextCmd = 'RunPlugin(' + _baseUrl+'?' + urllib.urlencode(params) + ')'
		contextMenuItems.append(('Play from YouTube',contextCmd))													
		item.addContextMenuItems(contextMenuItems, replaceItems=False)		
		params = {
			'handler': 'Play',
			'videoId': video['id'],			
		}
		xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?' + urllib.urlencode(params), isFolder=False, listitem=item)
	xbmcplugin.endOfDirectory(_handleId)
	

def handlerSeasons():
	xbmcplugin.setContent(_handleId, 'movies')
	for season in range(1, int(_params['seasons']) + 1):
		item = xbmcgui.ListItem(_params['contentName'] + ', Сезон ' + str(season))
		infoLabels = {}
		item.setInfo( type="Video", infoLabels=infoLabels )	
		params = {
			'handler': 'ContentVideos',
			'contentId': _params['contentId'],
			'season': season,
			'contentName': _params['contentName']
		}		
		xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?' + urllib.urlencode(params), isFolder=True, listitem=item)
	xbmcplugin.endOfDirectory(_handleId)	

	
def handlerSearchContent():
	content = rutube.searchContent(_params['searchStr'])
	if content is None:
		xbmcgui.Dialog().ok('Ошибка', 'К сожалению по вашему запросу ничего не найдено')
		return
	xbmcplugin.setContent(_handleId, 'movies')
	infoLabels = { 			
		"plot": content['type'] + "\n \n" + 'Сезоны: ' + str(content['seasons']) + ', Видео: ' + str(content['videos']) + "\n \n" + content['description']
	}	
	item = xbmcgui.ListItem(content['name'])
	item.setArt({'thumb': content["thumb"], 'poster': content["thumb"], 'fanart': content["thumb"]})
	item.setInfo( type="Video", infoLabels=infoLabels )	
	params = {
		'handler': 'Seasons',
		'contentId': content['id'],
		'contentName': content['name'],
		'seasons': content['seasons']
	}		
	xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?' + urllib.urlencode(params), isFolder=True, listitem=item)
	xbmcplugin.endOfDirectory(_handleId)	
	
	
def handlerSearch():
	kb = xbmc.Keyboard('', 'Search', True)
	kb.setHiddenInput(False)
	kb.doModal()
	if not (kb.isConfirmed()):
		return		
	searchStr = kb.getText()
	del kb		
	params = {
		'handler': _params['handlerRedirect'],
		'searchStr': searchStr
	}
	url=_baseUrl+'?' + urllib.urlencode( params )	
	xbmc.executebuiltin("Container.Update(" + url + ")")	

	
def handlerRoot():
	
	### Build base list ###
	pathImg = _path + '/resources/img/'
	xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?' + urllib.urlencode({'handler': 'Search', 'handlerRedirect': 'SearchContent'}), isFolder=True, listitem=xbmcgui.ListItem('Поиск', iconImage=pathImg+'search.png'))
	xbmcplugin.endOfDirectory(_handleId)
	
	

	
if 'handler' in _params.keys():
	globals()['handler' + _params['handler']]()
else:
	handlerRoot()
	
