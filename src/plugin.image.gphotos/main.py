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
	
_cookiesFolder = _addon.getSetting('cookiesFolder')


	
def handlerListAlbums():
	s = util.Session(_cookiesFolder)
	content = gphotos.getAlbums(s)
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
	s = util.Session(_cookiesFolder)
	content = gphotos.getAlbumPhotos(_params['id'], s)
	for data in content:
		item = xbmcgui.ListItem(str(data["name"]))
		item.setArt({'thumb': data["thumb"], 'poster': data["thumb"], 'fanart': data["thumb"]})
		item.setInfo(
			type='pictures',
			infoLabels={
				'title': data["name"],
				'picturepath': data["fullsize"],
				'exif:path':  data["fullsize"]
			}
		)			
		xbmcplugin.addDirectoryItem(handle=_handleId, url=data["fullsize"], listitem=item)			
	xbmcplugin.endOfDirectory(_handleId)			

	
def handlerRoot():
	handlerListAlbums()

	
if len(_cookiesFolder) == 0:
	xbmcgui.Dialog().ok('Error', 'Please configure settings')
else:	
	if 'handler' in _params.keys():
		globals()['handler' + _params['handler']]()
	else:
		handlerRoot()

