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
	
reload(sys)
sys.setdefaultencoding("utf-8")	
	
	
	
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
	


def getKeshetStream():
	import requests
	import json
	plurl = '/hls/live/512033/CH2LIVE_HIGH/index.m3u8'
	url = 'https://mass.mako.co.il/ClicksStatistics/entitlementsServicesV2.jsp'
	params = {
		'et': 'gt',
		'lp': plurl,
		'rv': 'AKAMAI',
		'dv': '6540b8dcb64fd310VgnVCM2000002a0c10acRCRD'
	}
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
		'Referer': 'https://www.mako.co.il/mako-vod-live-tv/VOD-6540b8dcb64fd31006.htm'
	}
	s = requests.Session()
	s.verify = False
	data = json.loads(s.get(url=url, params=params, headers=headers).text)
	ticket = data['tickets'][0]['ticket']
	url = 'https://keshethlslive-i.akamaihd.net' + plurl + '?' + ticket
	return url
	
	
def handlerPlay():

	if _params['name'] == 'קשת':
		_params['url'] = getKeshetStream()
		
	util.play(_params['url'],_params['name'])
#	item = xbmcgui.ListItem(_params['name'])
#	xbmc.Player().play(_params['url'], item)

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
