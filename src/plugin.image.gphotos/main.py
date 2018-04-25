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
	
	
def handlerListAlbums():
	content = gphotos.getAlbums(_cookiesGoogle)
	for data in content:
		item = xbmcgui.ListItem(data["name"])
		item.setArt({'thumb': data["thumb"], 'poster': data["thumb"], 'fanart': data["thumb"]})
		params = {
			'handler': 'ListAlbumPhotos',
			'id': data["id"],
		}						
		xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?' + urllib.urlencode(params), isFolder=True, listitem=item)
	xbmcplugin.endOfDirectory(_handleId)		

	
def handlerListAlbumPhotos():
	content = gphotos.getAlbumContent(_cookiesGoogle,_params['id'])
	for data in content['videos']:
		item = xbmcgui.ListItem(data['name'])
		item.setArt({'thumb': data["thumb"]})	
		item.setInfo(type='video', infoLabels={})			
		params = {
			'handler': 'Play',
			'url': data['url'],
			'name': data['name']
		}
		url = _baseUrl+'?' + urllib.urlencode(params)								
		xbmcplugin.addDirectoryItem(handle=_handleId, url=url, isFolder=True, listitem=item)
	for data in content['photos']:
		item = xbmcgui.ListItem(data['name'])
		item.setArt({'thumb': data["thumb"]})
		item.setInfo(type='pictures', infoLabels={
				'title': data['name'],
				'picturepath': data['url'],
				'exif:path':  data['url']
			}
		)			
		xbmcplugin.addDirectoryItem(handle=_handleId, url=data['url'], listitem=item)			
	xbmcplugin.endOfDirectory(_handleId)			

	
def handlerPlay():
	util.play(_params['url'], _params['name'])
	
	
def handlerRoot():
	handlerListAlbums()



if validateSettings():
	if 'handler' in _params.keys():
		globals()['handler' + _params['handler']]()
	else:
		handlerRoot()
