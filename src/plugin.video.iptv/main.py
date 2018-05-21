# coding: utf-8

import sys
import urlparse
import xbmcaddon
import gui



_baseUrl = sys.argv[0]
_handleId = int(sys.argv[1])
_params = dict(urlparse.parse_qsl(sys.argv[2][1:]))	
_addon = xbmcaddon.Addon()
_path = _addon.getAddonInfo('path') + '/'	
_epgFile = _addon.getSetting('epgFile')
_playlistFile = _addon.getSetting('playlistFile')
_iconsFolder = _addon.getSetting('iconsFolder')
_timezone = 'Asia/Jerusalem'

reload(sys)
sys.setdefaultencoding("utf-8")	

_mandatorySettings = [
	'epgFile', 
	'playlistFile', 
	'iconsFolder'
]	





def validateSettings():
	for setting in _mandatorySettings:
		if len(_addon.getSetting(setting))==0:
			xbmcgui.Dialog().ok('Error', 'Please configure settings')
			return False
	return True


#from datetime import datetime
#from pytz import timezone
#import xbmcgui

#fmt = "%Y-%m-%d %H:%M:%S %z"

# Current time in UTC
#now_utc = datetime.now(timezone('Asia/Jerusalem'))
#xbmcgui.Dialog().ok('Player', now_utc.strftime(fmt))	
	
	
if validateSettings():
	dialog = gui.DialogEPG(_playlistFile,_epgFile,_iconsFolder,_timezone)
	dialog.doModal()
	del dialog
