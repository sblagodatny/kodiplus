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
	for data in content:			
		name = data["name"] + ' [' + str (data["count"]) + ']'
		if data['privacy']=='Private':
			name = util.color(name,'orange') 
		item = xbmcgui.ListItem(name, iconImage=data["thumb"] )
		item.setProperty("IsPlayable","false")	
		params = {
			'handler': 'PlaylistVideos',
			'id': data["id"]			
		}						
		xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?' + urllib.urlencode(params), isFolder=True, listitem=item)


def listVideos(content):
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
			'privacy': data['privacy'],
			'live': live
		}		
		xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?' + urllib.urlencode(params), isFolder=False, listitem=item)
	
	
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
	item=xbmcgui.ListItem()
	cookies = s.cookies.get_dict(domain='.youtube.com')
	headers = {'Cookie': "; ".join([str(x)+"="+str(y) for x,y in cookies.items()])}	
	streams = youtube.getStreams(_params['id'], s)
	itag = util.firstMatch(youtube.itagsVod, streams.keys())
	if itag is None:
		itag = util.firstMatch(youtube.itagsLive, streams.keys())
		if itag is None:
			xbmcgui.Dialog().ok('Error', 'Unable to get stream')
			return			
	item.setPath(streams[itag] + '|' + urllib.urlencode(headers))
	xbmcplugin.setResolvedUrl(_handleId, True, listitem=item)			

	
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
	xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?' + urllib.urlencode({'handler': 'MyVideos'}), isFolder=True, listitem=xbmcgui.ListItem('My Videos', iconImage=pathImg+'myVideos.png'))
	xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?' + urllib.urlencode({'handler': 'MyPlaylists'}), isFolder=True, listitem=xbmcgui.ListItem('My Playlists', iconImage=pathImg+'myPlaylists.png'))
	xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?' + urllib.urlencode({'handler': 'SavedPlaylists'}), isFolder=True, listitem=xbmcgui.ListItem('Saved Playlists', iconImage=pathImg+'savedPlaylists.png'))
	xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?' + urllib.urlencode({'handler': 'Search', 'handlerRedirect': 'SearchVideos'}), isFolder=True, listitem=xbmcgui.ListItem('Search Videos', iconImage=pathImg+'searchVideos.png'))
	xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?' + urllib.urlencode({'handler': 'Search', 'handlerRedirect': 'SearchPlaylists'}), isFolder=True, listitem=xbmcgui.ListItem('Search Playlists', iconImage=pathImg+'searchPlaylists.png'))
	xbmcplugin.endOfDirectory(_handleId)

	
if len(_cookiesFolder) == 0:
	xbmcgui.Dialog().ok('Error', 'Please configure settings')
else:	
	if 'handler' in _params.keys():
		globals()['handler' + _params['handler']]()
	else:
		handlerRoot()

