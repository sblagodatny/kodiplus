# coding: utf-8

import sys
import urlparse
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs
import datetime
import util
import urllib
import os
import datetime



_baseUrl = sys.argv[0]
_handleId = int(sys.argv[1])
_params = dict(urlparse.parse_qsl(sys.argv[2][1:]))	
_addon = xbmcaddon.Addon()
_path = _addon.getAddonInfo('icon').replace('icon.png','')
	
_epgFile = _addon.getSetting('epgFile')
_playlistFile = _addon.getSetting('playlistFile')
_iconsFolder = _addon.getSetting('iconsFolder')
_forceMxPlayer = _addon.getSetting('forceMxPlayer')
	
	
	
	
def listChannels(channels, epg):
	xbmcplugin.setContent(_handleId, 'movies')
	for channel in channels:
		infoLabels = {}	
		if 'tvg_id' in channel.keys():
			try:
				program = util.xmltvGetCurrent(epg, channel['tvg_id'], util.nvld(channel, 'tvg_shift', None))
				infoLabels = {'plot': util.bold(program['title']) + '  [' + str(program['remaining']) + "] \n\n" + program['description']}
			except:
				None			
		contextMenuItems = []
		contextCmd = 'Container.Refresh()'
		contextMenuItems.append(('Refresh',contextCmd))
		if 'archive' in channel.keys():
			archive = channel['archive']
			archiveParams = None
			if '|' in archive:
				archiveParams = archive.split('|')[1]
				archive = archive.split('|')[0]
			params = {
				'handle': _handleId,
				'handler': 'ListCategories',
				'archive': archive
			}	
			if archiveParams is not None:
				params.update({'archiveParams': archiveParams})
			archiveAddonUrl = 'plugin://plugin.video.tvarchive/'
			contextCmd = 'ActivateWindow(Videos,' + archiveAddonUrl + '?' + urllib.urlencode(params) + ',return)'
			contextMenuItems.append(('Arhive',contextCmd))
		item = xbmcgui.ListItem(channel['name'])
		item.addContextMenuItems(contextMenuItems, replaceItems=True)
		if 'tvg_logo' in channel.keys():
			logo = _iconsFolder + channel['tvg_logo']
			item.setArt({'thumb': logo, 'poster': logo, 'fanart': logo})
		item.setInfo( type="Video", infoLabels=infoLabels )
		params = {
			'handler': 'Play',
			'name': channel['name'],
			'url': channel['url']
		}
		url = _baseUrl+'?' + urllib.urlencode(params)
		xbmcplugin.addDirectoryItem(handle=_handleId, url=url, isFolder=True, listitem=item)
	xbmcplugin.endOfDirectory(_handleId)
	
	
def handlerPlay():		
	if _forceMxPlayer =='true':
		cmd=[
			'am','start','-n','com.mxtech.videoplayer.ad/.ActivityScreen','-d',_params['url'],
			'--es','title',_params['name'],
#			'--esa', 'User-Agent,Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
			'--activity-clear-task','--user','0'
		]
		import subprocess
		p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdout, stderr = p.communicate()
#		xbmcgui.Dialog().ok('Finished', stdout, stderr)
	else:
		item=xbmcgui.ListItem(_params['name'])
		item.setPath(_params['url'])
		xbmc.Player().play(_params['url'],item)

def getEPG():
	if os.path.isfile(_path + '/epg'):
		mtime = datetime.datetime.fromtimestamp(os.path.getmtime(_path + '/epg'))
		midnight = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
		if mtime > midnight:
			epg = util.fileToObj(_path + '/epg')
			return epg
	epg = util.xmltvParse(_epgFile)
	util.objToFile(epg,_path + '/epg')
	return epg

	
def handlerRoot():
	channels = util.m3uChannels(_playlistFile)
	listChannels(channels, getEPG())
	
	
if len(_playlistFile) == 0 or len(_iconsFolder) == 0:
	xbmcgui.Dialog().ok('Error', 'Please configure settings')
else:	
	if 'handler' in _params.keys():
		globals()['handler' + _params['handler']]()
	else:
		handlerRoot()
