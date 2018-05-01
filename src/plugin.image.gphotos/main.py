# coding: utf-8

import sys
import urlparse
import xbmc
import xbmcgui
import xbmcplugin
import xbmcvfs
import urllib
import xbmcaddon
import util
import gphotos


_baseUrl = sys.argv[0]
_handleId = int(sys.argv[1])
_params = dict(urlparse.parse_qsl(sys.argv[2][1:]))	
_addon = xbmcaddon.Addon()
_path = _addon.getAddonInfo('icon').replace('icon.png','')

_dataFolder = _addon.getSetting('cookiesFolder')
_cookiesGoogle = _dataFolder + '/cookies'



def validateSettings():
	if len(_dataFolder)==0: 
		xbmcgui.Dialog().ok('Error', 'Please configure settings')
		return False
	return True
	

def listAlbums(albums):	
	for data in albums:
		name = util.bold(data["name"])
		if data['sharedKey'] is not None:
			name = util.color(name, 'orange')
		item = xbmcgui.ListItem(name)
		item.setArt({'thumb': data["thumb"], 'poster': data["thumb"], 'fanart': data["thumb"]})
		params = {
			'handler': 'ListAlbum',
			'id': data["id"],
			'sharedKey': data['sharedKey']
		}						
		xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?' + urllib.urlencode(params), isFolder=True, listitem=item)

		
def listVideos(videos):
	for data in videos:
		name = 'Video ' + str(data['ts'])
		item = xbmcgui.ListItem(name)
		item.setArt({'thumb': data["thumb"]})	
		item.setInfo(type='video', infoLabels={})			
		params = {
			'handler': 'Play',
			'url': data['url'],
			'name': name
		}
		url = _baseUrl+'?' + urllib.urlencode(params)								
		xbmcplugin.addDirectoryItem(handle=_handleId, url=url, isFolder=True, listitem=item)

def listPhotos(photos):
	for data in photos:
		name = 'Photo ' + str(data['ts'])
		item = xbmcgui.ListItem(name)
		item.setArt({'thumb': data["thumb"]})
		item.setInfo(type='pictures', infoLabels={
				'title': name,
				'picturepath': data['url'],
				'exif:path':  data['url']
			}
		)			
		xbmcplugin.addDirectoryItem(handle=_handleId, url=data['url'], listitem=item)			


def handlerAlbums():
	xbmcplugin.setContent(_handleId, 'images')
	content = gphotos.getAlbums(_cookiesGoogle)
	listAlbums(content)
	xbmcplugin.endOfDirectory(_handleId)
	
		
def handlerListAlbum():
	xbmcplugin.setContent(_handleId, 'images')
	sharedKey = None
	if len(_params['sharedKey']) > 6:
		sharedKey = _params['sharedKey']
	content = gphotos.getAlbumContent(_cookiesGoogle,_params['id'],sharedKey)
	listVideos(content['videos'])
	listPhotos(content['photos'])
	xbmcplugin.endOfDirectory(_handleId)			

	
def handlerPlay():
	util.play(_params['url'], _params['name'])
	

def handlerSearchResults():
	xbmcplugin.setContent(_handleId, 'images')
	content = gphotos.search(_cookiesGoogle, _params['searchStr'])
	listAlbums(content['albums'])
	listVideos(content['videos'])
	listPhotos(content['photos'])
	xbmcplugin.endOfDirectory(_handleId)			


def handlerSearch():
	kb = xbmc.Keyboard('', 'Поиск', True)
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
	pathImg = _path + '/resources/img/'	
	rootLinks = [		
		{'name': 'Альбомы', 'urlParams': {'handler': 'Albums'}, 'icon': pathImg+'Albums.png'},
		{'name': 'Поиск', 'urlParams': {'handler': 'Search', 'handlerRedirect': 'SearchResults'}, 'icon': pathImg+'Search.png'}		
	]
	for rootLink in rootLinks:
		item=xbmcgui.ListItem(rootLink['name'], iconImage=rootLink['icon'])		
		xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?'+urllib.urlencode(rootLink['urlParams']), isFolder=True, listitem=item)
	xbmcplugin.endOfDirectory(_handleId)	
	

if validateSettings():
	if 'handler' in _params.keys():
		globals()['handler' + _params['handler']]()
	else:
		handlerRoot()
