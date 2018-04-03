# coding: utf-8

import sys
import urlparse
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import urllib
import urllib2
import youtube
import util





_baseUrl = sys.argv[0]
_handleId = int(sys.argv[1])
_params = dict(urlparse.parse_qsl(sys.argv[2][1:]))	
_addon = xbmcaddon.Addon()
_path = _addon.getAddonInfo('icon').replace('icon.png','')
	

_useDash=_addon.getSetting('useDash')
_cookiesFolder = _addon.getSetting('cookiesFolder')

_cookiesFile = _cookiesFolder + '/cookies'

reload(sys)
sys.setdefaultencoding("utf-8")	

def validateSettings():
	if len(_cookiesFolder) == 0:
		xbmcgui.Dialog().ok('Error', 'Please configure settings')
		return False	
	return True
	
def listPlaylists(content):
	xbmcplugin.setContent(_handleId, 'movies')
	for data in content:			
		name = data["name"] + ' [' + str (data["count"]) + ']'
		if data['privacy']=='Private':
			name = util.color(name,'orange') 
		item = xbmcgui.ListItem(name)
		item.setArt({'thumb': data["thumb"], 'poster': data["thumb"], 'fanart': data["thumb"]})
		item.setProperty("IsPlayable","false")	
		params = {
			'handler': 'PlaylistVideos',
			'id': data["id"]			
		}						
		xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?' + urllib.urlencode(params), isFolder=True, listitem=item)


def listVideos(content):
	xbmcplugin.setContent(_handleId, 'movies')
	autoplay = []
	autoplayIndex = 0
	for data in content:
		contextMenuItems=[]
		contextCmd = 'RunPlugin(' + _baseUrl+'?' + urllib.urlencode({'handler': 'AutoPlay', 'autoplayIndex': str(autoplayIndex)}) + ')'
		contextMenuItems.append(('Auto Play',contextCmd))	
		infoLabels = { 			
			"plot": '.' + "\n\n\n\n\n" + 
				util.bold('Duration: ') + data['duration'] + "\n\n" + 
				util.bold('Date: ') + data['publishedTime'] + "\n\n" + 
				util.bold('Views: ') + data['viewCount'] + "\n\n" + 
				util.bold('Owner: ') + data['owner'] + "\n\n" + 
				util.bold('Privacy: ') + data['privacy'] 
		}
		name = data["name"]		
		item = xbmcgui.ListItem(name)
		item.setArt({'thumb': data["thumb"], 'poster': data["thumb"], 'fanart': data["thumb"]})
		item.setProperty("IsPlayable","true")
		item.setInfo( type="Video", infoLabels=infoLabels )	
		item.addContextMenuItems(contextMenuItems, replaceItems=True)
		live='False'
		if data['duration'] == '':
			live = 'True'
		params = {
			'handler': 'Play',
			'id': data['id'],
			'name': data['name']
		}
		autoplay.append(params)
		autoplayIndex = autoplayIndex + 1
		xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?' + urllib.urlencode(params), isFolder=True, listitem=item)
	util.objToFile(autoplay, _path + '/autoplay')
	
	
def handlerSearchPlaylists():
	content = youtube.searchPlaylists(_params['searchStr'], _cookiesFile)
	listPlaylists(content)
	xbmcplugin.endOfDirectory(_handleId)		
	

def handlerSearchVideos():
	content = youtube.searchVideos(_params['searchStr'], _cookiesFile)
	listVideos(content)	
	xbmcplugin.endOfDirectory(_handleId)
	
	
def handlerPlaylistVideos():	
	content = youtube.getPlaylistVideos(_params['id'], _cookiesFile)
	listVideos(content)	
	xbmcplugin.endOfDirectory(_handleId)		

	
def handlerMyVideos():	
	content = youtube.getMyVideos(_cookiesFile)
	listVideos(content)
	xbmcplugin.endOfDirectory(_handleId)	


def handlerMyPlaylists():	
	content = youtube.getMyPlaylists(_cookiesFile)
	listPlaylists(content)
	xbmcplugin.endOfDirectory(_handleId)		


def handlerSavedPlaylists():	
	content = youtube.getSavedPlaylists(_cookiesFile)
	listPlaylists(content)
	xbmcplugin.endOfDirectory(_handleId)			
	
	
def handlerAutoPlay():		
	autoplayIndex = int(_params['autoplayIndex'])
	autoplay = util.fileToObj(_path + '/autoplay')
	for i in range(autoplayIndex, len(autoplay)):
		_params.update(autoplay[i])
		handlerPlay()
		if i < len(autoplay)-1:
			if xbmcgui.Dialog().yesno(heading='Playing next', line1=' ', line3=autoplay[i+1]['name'], yeslabel='Stop', nolabel='Play', autoclose=5000):
				break
			
	
def handlerPlay():	
	streams, cookies = youtube.getStreams(_params['id'], _cookiesFile)
	itag = util.firstMatch(youtube.itagsVideo, streams.keys())
	if itag is None:
		itag = util.firstMatch(youtube.itagsLive, streams.keys())
		if itag is None:
			xbmcgui.Dialog().ok('Error', 'Unable to get stream')
			return			
	url = streams[itag]
	util.play(url, _params['name'], util.headerCookie(cookies))	
	
	
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
	items = [
		{'name': 'My Videos', 'params': {'handler': 'MyVideos'}, 'thumb': 'myVideos.png'},
		{'name': 'My Playlists', 'params': {'handler': 'MyPlaylists'}, 'thumb': 'myPlaylists.png'},
		{'name': 'Saved Playlists', 'params': {'handler': 'SavedPlaylists'}, 'thumb': 'savedPlaylists.png'},
		{'name': 'Search Videos', 'params': {'handler': 'Search', 'handlerRedirect': 'SearchVideos'}, 'thumb': 'searchVideos.png'},
		{'name': 'Search Playlists', 'params': {'handler': 'Search', 'handlerRedirect': 'SearchPlaylists'}, 'thumb': 'searchPlaylists.png'},
	]
	for item in items:
		li = xbmcgui.ListItem(item['name'])
		img = _path + '/resources/img/' + item["thumb"]
		li.setArt({'thumb': img, 'poster': img})
		xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?' + urllib.urlencode(item['params']), isFolder=True, listitem=li)
	xbmcplugin.endOfDirectory(_handleId)


		
if validateSettings():
	if 'handler' in _params.keys():
		globals()['handler' + _params['handler']]()
	else:
		handlerRoot()

