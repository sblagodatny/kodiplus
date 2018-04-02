# coding: utf-8

import sys
import os
import urlparse
import xbmc
import xbmcgui
import xbmcplugin
import xbmcvfs
import urllib
import urllib2
import kinopoisk
import kinopoiskplus
import rutracker
import transmission
import xbmcaddon
import util
import gui
import time
import xbmcvfs
import stat
import cache
import traceback
import requests
import watchlog



_baseUrl = sys.argv[0]
_handleId = int(sys.argv[1])
_params = dict(urlparse.parse_qsl(sys.argv[2][1:], keep_blank_values=True))	
_addon = xbmcaddon.Addon()
_path = _addon.getAddonInfo('path') + '/'


_cookiesFolder = _addon.getSetting('cookiesFolder')
_kinopoiskUser = _addon.getSetting('kinopoiskUser')
_kinopoiskPassword = _addon.getSetting('kinopoiskPassword')
_rutrackerUser = _addon.getSetting('rutrackerUser')
_rutrackerPassword = _addon.getSetting('rutrackerPassword')
_transmissionUrl = _addon.getSetting('transmissionUrl')
_transmissionDownloadsFolder = _addon.getSetting('transmissionDownloadsFolder')
_cacheFolder = _addon.getSetting('cacheFolder')
_watchedFolder = _addon.getSetting('watchedFolder')

_cookiesKinopoisk = _cookiesFolder + '/cookiesKinopoisk'
_cookiesRutracker = _cookiesFolder + '/cookiesRutracker'

_refreshFlag = _path + '/refresh'


reload(sys)  
sys.setdefaultencoding('utf8')	


def validateSettings():
	if len(_cookiesFolder)==0 or len(_kinopoiskUser)==0 or len(_kinopoiskPassword)==0 or len(_rutrackerUser)==0 or len(_rutrackerPassword)==0 or len(_transmissionUrl)==0 or len(_transmissionDownloadsFolder)==0 or len(_cacheFolder)==0 or len(_watchedFolder)==0: 
		xbmcgui.Dialog().ok('Error', 'Please configure settings')
		return False
	return True


def getDetails(id, full=False):
	details=cache.get(id, _cacheFolder)
	if details is not None or not full:
		return details
	details = kinopoisk.getDetails(_cookiesKinopoisk, id)
	cache.set(id, details, _cacheFolder)		
	return details

	
def listContent(content, folder=-1):
	cache.init(_cacheFolder,_path)	
	xbmcplugin.setContent(_handleId, 'movies')
	for item in content:		
		name = item['name'] + ' (' + item['year'] + ')' 
		li = xbmcgui.ListItem(name)	
		contextMenuItems = []			
		infoLabels = {}	
		infoLabels['year'] = item['year']
		details=getDetails(item['id'],False)
		if details is not None:
			infoLabels['plot'] = details['description']
			if details['rating'] != '':
				infoLabels['rating'] = float(details['rating'])
			infoLabels['genre'] = ' '.join(details['genre'])
			infoLabels['country'] = ' '.join(details['country'])
			li.setCast(details['actors'] + details['directors'])
		contextCmd = 'RunPlugin(' + _baseUrl+'?' + urllib.urlencode({'handler': 'Info', 'id': item['id'], 'ready': str(details is not None)}) + ')'
		contextMenuItems.append(('Info',contextCmd))	
		if len(item['myrating']) > 0:
			infoLabels['userrating'] = float(item['myrating'])
			infoLabels['playcount'] = 1
			contextCmd = 'RunPlugin(' + _baseUrl+'?' + urllib.urlencode({'handler': 'SetWatchedKinopoisk', 'id': item['id'], 'watched': 'False'}) + ')'
			contextMenuItems.append(('UnWatched',contextCmd))	
		else:
			infoLabels['playCount'] = 0
			contextCmd = 'RunPlugin(' + _baseUrl+'?' + urllib.urlencode({'handler': 'SetWatchedKinopoisk', 'id': item['id'], 'watched': 'True'}) + ')'
			contextMenuItems.append(('Watched',contextCmd))	
		contextCmd = 'RunPlugin(' + _baseUrl+'?' + urllib.urlencode({'handler': 'ManageFolders', 'id': item['id']}) + ')'
		contextMenuItems.append(('Manage Folders',contextCmd))	
		li.setArt({'thumb': kinopoisk.getThumb(item['id']), 'poster': kinopoisk.getPoster(item['id']), 'fanart': kinopoisk.getPoster(item['id'])})
		li.setInfo( type="Video", infoLabels=infoLabels )											
		li.addContextMenuItems(contextMenuItems, replaceItems=True)		
		params = {'id': item['id'], 'handler': 'ListTorrents', 'name': item['name'], 'year': item['year'], 'myrating': item['myrating']}
		xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?' + urllib.urlencode(params), isFolder=True, listitem=li)
	xbmcplugin.endOfDirectory(_handleId)

	

def handlerInfo():
	if _params['ready'] == 'True':
		xbmc.executebuiltin('Action(info)')
	else:
		xbmc.executebuiltin( "ActivateWindow(busydialog)" )				
		details=getDetails(_params['id'],True)
		xbmc.executebuiltin( "Dialog.Close(busydialog)" )
		xbmc.executebuiltin('Container.Refresh')
	
	
	
def handlerListFolders():
	folders = kinopoisk.getFolders(_cookiesKinopoisk)
	for id, name in folders.iteritems():
		item=xbmcgui.ListItem(name)
		params = {'handler': 'ListFolder', 'folder': id}
		xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?'+urllib.urlencode(params), isFolder=True, listitem=item)
	xbmcplugin.endOfDirectory(_handleId)

	
def handlerListFolder():
	content = kinopoisk.getFolderContent(_cookiesKinopoisk, _params['folder'])
	listContent(content)
	
	

	



#def handlerFilterTorrentFiles():
#	torrent = searchDownloads(hashString=_params['hashString'])[0]['torrent']
#	list = getTorrentVideoFilesList(torrent)
#	selected = []
#	for i in range (0, len(list)):
#		d = eval(list[i].getProperty('code'))	
#		if _params['selected'] == 'current':			
#			if d['wanted']:
#				selected.append(i)
#		else:
#			if not d['playCount'] > 0:
#				selected.append(i)		
#	result = xbmcgui.Dialog().multiselect("Included files", list, preselect=selected)			
#	if result is None:
#		return
#	unselected = []
#	for i in range (0, len(list)):
#		if i not in result:
#			d = eval(list[i].getProperty('code'))
#			unselected.append(d['idFile'])	
#	s = util.Session(_cookiesFolder)
#	transmission.modify(s, _transmissionUrl, _params['hashString'], {'files-wanted': []})
#	if len(unselected) > 0:
#		transmission.modify(s, _transmissionUrl, _params['hashString'], {'files-unwanted': unselected})
	
	
def handlerListTorrent():
	xbmcplugin.setContent(_handleId, 'movies')
	pathImg = _path + '/resources/img/'	
	watchlog.init(_watchedFolder,_path)	
	data = transmission.get(_transmissionUrl, _params['hashString'])[0]
	files = sorted(data['files'], key=lambda k: k['name']) 
	for file in files:
		path = os.path.abspath(_transmissionDownloadsFolder + file['name']).encode('utf8')
		url = 'file:' + urllib.pathname2url(path)
		name = util.fileName(urllib.unquote(url))		
		if util.fileExt(path.lower()) not in ['avi','mkv','mp4']:
			continue
		infoLabels = {}
		contextMenuItems = []
		if watchlog.isWatched(_watchedFolder, _baseUrl, _params['hashString'] + '|' + name):
			infoLabels['playcount'] = 1
			contextCmd = 'RunPlugin(' + _baseUrl+'?' + urllib.urlencode({'handler': 'SetWatched', 'item': _params['hashString'] + '|' + name, 'watched': 'false'}) + ')'
			contextMenuItems.append(('UnWatched',contextCmd))
		else:
			infoLabels['playcount'] = 0
			contextCmd = 'RunPlugin(' + _baseUrl+'?' + urllib.urlencode({'handler': 'SetWatched', 'item': _params['hashString'] + '|' + name, 'watched': 'true'}) + ')'
			contextMenuItems.append(('Watched',contextCmd))
		item=xbmcgui.ListItem(name, iconImage=pathImg + 'video.png')
		item.addContextMenuItems(contextMenuItems, replaceItems=True)	
		item.setInfo( type="Video", infoLabels=infoLabels )	
		params = {
			'handler': 'Play',
			'url': url,
			'name': name,
			'hashString': _params['hashString']
		}
		url = _baseUrl+'?' + urllib.urlencode(params)								
		xbmcplugin.addDirectoryItem(handle=_handleId, url=url, isFolder=True, listitem=item)
	xbmcplugin.endOfDirectory(_handleId)
	
	
	
def handlerPlay():
	watchlog.setWatched(_watchedFolder, _baseUrl, _params['hashString'] + '|' + _params['name'])
	util.play(_params['url'], _params['name'])
	xbmc.executebuiltin("Container.Refresh()")
	
	
	
def handlerAddTorrent():	
	searchStr = _params['name']
	strict = []
	if not kinopoisk.isSeries(_params['name']):
		searchStr = searchStr + ' ' + _params['year']
	torrents = rutracker.search(_cookiesRutracker, searchStr, strict)
	downloads = getDownloads()
	dtorrents = []
	if _params['id'] in downloads.keys():
		dtorrents = downloads[_params['id']]['torrents'].values()
	values = []
	for torrent in torrents:				
		if torrent['name'] not in dtorrents:
			values.append ('[' + str(round((float(torrent["size"]) / (1024*1024*1024)),2)) + 'Gb, ' + torrent["seeds"] + ' Seeds] ' + torrent['name'] )
	result = xbmcgui.Dialog().select("Torrents", values)			
	if result==-1:
		return
	torrent = torrents[result]	
	hashString = transmission.add(_transmissionUrl, torrent['url'], _cookiesRutracker)
	if _params['id'] not in downloads.keys():
		downloads.update({
			_params['id']: {
				'name': _params['name'],
				'year': _params['year'],
				'myrating': _params['myrating'],
				'torrents': {}
			}
		})
	downloads[_params['id']]['torrents'][hashString] = torrent['name']
	setDownloads(downloads)
	xbmc.executebuiltin('Container.Refresh')
	
	
def log(message,loglevel=xbmc.LOGNOTICE):
	xbmc.log('plugin.video.kinopoisk' + " : " + message,level=loglevel)
		
	
def handlerSetWatchedKinopoisk():
	kinopoisk.setWatched(_cookiesKinopoisk, _params['id'], eval(_params['watched']))	
	downloads = getDownloads()
	if _params['id'] in downloads.keys():
		if _params['watched']:
			downloads[_params['id']]['myrating']='7'
		else:
			downloads[_params['id']]['myrating']=''
		setDownloads(downloads)
	xbmc.executebuiltin('Container.Refresh')			

	
def handlerSetWatched():		
	if _params['watched'] == 'true':
		watchlog.setWatched(_watchedFolder, _baseUrl, _params['item'])
	else:
		watchlog.setUnWatched(_watchedFolder,_baseUrl, _params['item'])
	xbmc.executebuiltin("Container.Refresh()")

	
def handlerManageFolders():
	xsrftoken, folders = kinopoisk.getItemFolders(_cookiesKinopoisk, _params['id'])
	folderslist = []
	selected = []
	for i in range(0,len(folders)):
		folderslist.append(xbmcgui.ListItem(folders[i]['name']))
		if folders[i]['assigned']:
			selected.append(i)
	selected = xbmcgui.Dialog().multiselect("Folders", folderslist, preselect=selected)			
	if selected is None:
		return
	for i in range(0,len(folders)):
		if i in selected:
			folders[i]['assigned'] = True
		else:
			folders[i]['assigned'] = False
	kinopoisk.manageFolders(_cookiesKinopoisk, _params['id'], folders, xsrftoken)
	

	
def handlerSearchResults():	
	content = eval(_params['content'])
	listContent(content)
	
	
def handlerSearch():		
	w = gui.DialogSearch("DialogSearch.xml", _path , "Default")
	w.doModal()
	result = w.result()
	del w
	if result is None:
		return
	if result['name'] is not None:
		content = kinopoisk.searchByTitle(_cookiesKinopoisk, title = result['name'], contentType=result['action'])
	else:			
		content = kinopoisk.searchByParams(_cookiesKinopoisk, contentType=result['action'], hideWatched=True, hideInFolders=True, genre=result['genres'], years=result['years'], countries=result['countries'])			
	params = {
		'handler': 'SearchResults',
		'content': str(content)
	}
	url=_baseUrl+'?' + urllib.urlencode( params )	
	xbmc.executebuiltin("Container.Update(" + url + ")")


def handlerMonitorTorrent():
	w = gui.DialogDownloadStatus("DialogDownloadStatus.xml",_path )	
	w.setData({
		'hashString': _params['hashString'], 
		'transmissionUrl': _transmissionUrl, 
		'torrentName': _params['torrentName']
	})
	w.doModal()
	w.stop()
	del w
	xbmc.executebuiltin('Container.Refresh')

def handlerRemoveTorrent():
	transmission.remove(_transmissionUrl, _params['hashString'], True)
	downloads = getDownloads()
	hashString = _params['hashString']
	del downloads[_params['id']]['torrents'][_params['hashString']]
	if not downloads[_params['id']]['torrents']:
		del downloads[_params['id']]
	setDownloads(downloads)
	xbmc.executebuiltin('Container.Refresh')
	
	
def handlerListTorrents():
	downloads = getDownloads()
	pathImg = _path + '/resources/img/'	
	content = []
	downloads = getDownloads()
	torrents = {}
	if _params['id'] in downloads.keys():
		torrents = downloads[_params['id']]['torrents']
	for hashString, name in torrents.iteritems():					
		contextMenuItems = []
		data = transmission.get(_transmissionUrl, [hashString])[0]
		if data['percentDone'] == 1:
			params = {
				'handler': 'ListTorrent',
				'hashString': hashString
			}
		else:
			params = {
				'handler': 'MonitorTorrent',
				'hashString': hashString,
				'torrentName': name
			}
			name = '[' + str(int(float(data['percentDone'])*100)) + '%] '  + name
			contextCmd = 'RunPlugin(' + _baseUrl+'?' + urllib.urlencode({'handler': 'FilterTorrent', 'hashString': hashString}) + ')'
			contextMenuItems.append(('Filter',contextCmd))	
		contextCmd = 'RunPlugin(' + _baseUrl+'?' + urllib.urlencode({'handler': 'RemoveTorrent', 'id': _params['id'], 'hashString': hashString}) + ')'
		contextMenuItems.append(('Remove',contextCmd))	
		item=xbmcgui.ListItem(name, iconImage=pathImg + 'torrent.png')
		item.addContextMenuItems(contextMenuItems, replaceItems=True)						
		xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?'+urllib.urlencode(params), isFolder=True, listitem=item)
	item=xbmcgui.ListItem('Add Torrent', iconImage=pathImg + 'addtorrent.png')		
	params = {'handler': 'AddTorrent', 'id': _params['id'], 'name': _params['name'], 'year': _params['year'], 'myrating': _params['myrating']}
	xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?'+urllib.urlencode(params), isFolder=True, listitem=item)
	xbmcplugin.endOfDirectory(_handleId)
			
	
def getDownloads():
	path = _path + '/downloads'
	if not os.path.isfile(path):
		return {}
	return util.fileToObj(path)

def setDownloads(downloads):
	path = _path + '/downloads'
	util.objToFile(downloads, path)
	
def handlerDownloads():
	content = []
	downloads = getDownloads()
	for id, data in downloads.iteritems():
		content.append({
			'id': id,
			'name': data['name'],
			'year': data['year'],
			'myrating': data['myrating']
		})
	listContent(content)


def loginKinopoisk():
	if os.path.isfile(_cookiesKinopoisk):
		return
	kinopoiskplus.login(_cookiesKinopoisk, _kinopoiskUser, _kinopoiskPassword)

def loginRutracker():
	if os.path.isfile(_cookiesRutracker):
		return
	rutracker.login(_cookiesRutracker, _rutrackerUser, _rutrackerPassword)
	
	
def handlerRoot():	
	loginKinopoisk()
	loginRutracker()
	pathImg = _path + '/resources/img/'	
	rootLinks = [
		{'name': 'Search', 'urlParams': {'handler': 'Search'}, 'icon': pathImg+'Search.png'},
		{'name': 'Downloads', 'urlParams': {'handler': 'Downloads'}, 'icon': pathImg+'Downloads.png'},
		{'name': 'Folders', 'urlParams': {'handler': 'ListFolders'}, 'icon': pathImg+'Folders.png'}
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
