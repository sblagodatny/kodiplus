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


reload(sys)
sys.setdefaultencoding("utf-8")	

	
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
	for data in content:
		infoLabels = { 			
			"duration": data["duration"],
			"director": data["user"],			
		}
		name = data["name"]
		if data['privacy'] == 'Private':
			name = '[COLOR orange]' + name + '[/COLOR]'		
		item = xbmcgui.ListItem(name)
		item.setArt({'thumb': data["thumb"], 'poster': data["thumb"], 'fanart': data["thumb"]})
		item.setProperty("IsPlayable","true")
		item.setInfo( type="Video", infoLabels=infoLabels )	
		live='False'
		if data['duration'] == '':
			live = 'True'
		params = {
			'handler': 'Play',
			'id': data['id'],
			'name': data['name']
		}		
		xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?' + urllib.urlencode(params), isFolder=True, listitem=item)
	
	
def handlerSearchPlaylists():
	s = util.Session(_cookiesFolder)
	content = youtube.searchPlaylists(_params['searchStr'], s)
	listPlaylists(content)
	xbmcplugin.endOfDirectory(_handleId)		
	

def handlerSearchVideos():
	s = util.Session(_cookiesFolder)
	content = youtube.searchVideos(_params['searchStr'], s)
	listVideos(content)	
	xbmcplugin.endOfDirectory(_handleId)
	
	
def handlerPlaylistVideos():	
	s = util.Session(_cookiesFolder)
	content = youtube.getPlaylistVideos(_params['id'], s)
	listVideos(content)	
	xbmcplugin.endOfDirectory(_handleId)		

	
def handlerMyVideos():	
	s = util.Session(_cookiesFolder)
	content = youtube.getMyVideos(s)
	listVideos(content)
	xbmcplugin.endOfDirectory(_handleId)	


def handlerMyPlaylists():	
	s = util.Session(_cookiesFolder)
	content = youtube.getMyPlaylists(s)
	listPlaylists(content)
	xbmcplugin.endOfDirectory(_handleId)		


def handlerSavedPlaylists():	
	s = util.Session(_cookiesFolder)
	content = youtube.getSavedPlaylists(s)
	listPlaylists(content)
	xbmcplugin.endOfDirectory(_handleId)			
	
	
def handlerPlay():	
	s = util.Session(_cookiesFolder)
	streams = youtube.getStreams(_params['id'], s)
	itag = util.firstMatch(youtube.itagsVideo, streams.keys())
	if itag is None:
		itag = util.firstMatch(youtube.itagsLive, streams.keys())
		if itag is None:
			xbmcgui.Dialog().ok('Error', 'Unable to get stream')
			return			
	url = streams[itag]
	cookies = s.cookies.get_dict(domain='.youtube.com')
	headers = {'Cookie': "; ".join([str(x)+"="+str(y) for x,y in cookies.items()])}	
	util.play(url, _params['name'], headers)	

	
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

	
if len(_cookiesFolder) == 0:
	xbmcgui.Dialog().ok('Error', 'Please configure settings')
else:	
	if 'handler' in _params.keys():
		globals()['handler' + _params['handler']]()
	else:
		handlerRoot()

