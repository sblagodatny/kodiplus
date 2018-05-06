# coding: utf-8

import sys
import urlparse
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import urllib
import urllib2
import google
import util





_baseUrl = sys.argv[0]
_handleId = int(sys.argv[1])
_params = dict(urlparse.parse_qsl(sys.argv[2][1:]))	
_addon = xbmcaddon.Addon()
_path = _addon.getAddonInfo('icon').replace('icon.png','')
	

_mandatorySettings = ['googleUser', 'googlePassword', 'cookiesFolder']	
	
_googleUser=_addon.getSetting('googleUser')
_googlePassword=_addon.getSetting('googlePassword')
_cookiesPath = _addon.getSetting('cookiesFolder') + '/cookies'



def validateSettings():
	for setting in _mandatorySettings:
		if len(_addon.getSetting(setting))==0:
			xbmcgui.Dialog().ok('Error', 'Please configure settings')
			return False
	return True



def handlerLogin():
	google.login(_cookiesPath,_googleUser,_googlePassword)
	xbmcgui.Dialog().ok(_googleUser, 'Logged in successfully')


def handlerRoot():
	### Build base list ###
	xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?' + urllib.urlencode({'handler': 'Login'}), isFolder=True, listitem=xbmcgui.ListItem('Login'))
	xbmcplugin.endOfDirectory(_handleId)

	


if validateSettings():
	if 'handler' in _params.keys():
		globals()['handler' + _params['handler']]()
	else:
		handlerRoot()
	
