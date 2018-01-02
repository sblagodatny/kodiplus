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
import xbmcdb



_baseUrl = sys.argv[0]
_handleId = int(sys.argv[1])
_params = dict(urlparse.parse_qsl(sys.argv[2][1:], keep_blank_values=True))	
_addon = xbmcaddon.Addon()
_path = _addon.getAddonInfo('path') + '/'

_cookiesFolder = util.nvls(_addon.getSetting('cookiesFolder'),_path)
_kinopoiskUser = util.nvls(_addon.getSetting('kinopoiskUser'),'')
_kinopoiskPassword = util.nvls(_addon.getSetting('kinopoiskPassword'),'')
_rutrackerUser = util.nvls(_addon.getSetting('rutrackerUser'),'')
_rutrackerPassword = util.nvls(_addon.getSetting('rutrackerPassword'),'')
_transmissionUrl = util.nvls(_addon.getSetting('transmissionUrl'),'http://localhost/transmission/rpc')
_transmissionDownloadsFolder = util.nvls(_addon.getSetting('transmissionDownloadsFolder'),_path)
_cacheFolder = util.nvls(_addon.getSetting('cacheFolder'),_path)
_cacheAge = int(_addon.getSetting('cacheAge'))

reload(sys)  
sys.setdefaultencoding('utf8')	



def searchDownloads(downloads=None, id=None, season=None, hashString = None):
	if downloads is None:
		s = util.Session(_cookiesFolder)	
		downloads = transmission.get(s, _transmissionUrl, _transmissionDownloadsFolder)
	result = []
	for download in downloads:
		if 'metadata' not in download.keys():
			continue
		if id is not None:
			if download['metadata']['id'] != id:
				continue
		if season is not None:
			if download['metadata']['season'] != season:
				continue	
		if hashString is not None: 
			if download['torrent']['hashString'] != hashString:
				continue
		result.append(download)
	return result	
	

	
def listContent(content, folder=-1):
	s = util.Session(_cookiesFolder)
	c = cache.init(_cacheFolder)	
	downloads = transmission.get(s, _transmissionUrl, _transmissionDownloadsFolder)
	xbmcplugin.setContent(_handleId, 'movies')
	for id in content:
		contextMenuItems = []
		contextCmd = 'RunPlugin(' + _baseUrl+'?' + urllib.urlencode({'handler': 'Info'}) + ')'
		contextMenuItems.append(('Info',contextCmd))
		if folder == -1:
			contextCmd = 'RunPlugin(' + _baseUrl+'?' + urllib.urlencode({'handler': 'FolderAdd', 'id': id}) + ')'
			contextMenuItems.append(('Add to Folder',contextCmd))
		else:
			contextCmd = 'RunPlugin(' + _baseUrl+'?' + urllib.urlencode({'handler': 'FolderRemove', 'id': id, 'folder': folder}) + ')'
			contextMenuItems.append(('Remove from Folder',contextCmd))
			contextCmd = 'RunPlugin(' + _baseUrl+'?' + urllib.urlencode({'handler': 'FolderMove', 'id': id, 'folder': folder}) + ')'
			contextMenuItems.append(('Move to Folder',contextCmd))	
		infoLabels = {'playCount':0}	
		details=cache.get(c, id)
		if details is None:
			details = kinopoisk.getDetails(s, id)
			cache.set(c, id, details)			
		name = details['name']
		if 'nameOrig' in details.keys():
			name = name + ' / ' + details['nameOrig']
		infoLabels['plot'] = details['description']
		if details['rating'] != '':
			infoLabels['rating'] = float(details['rating'])
		infoLabels['genre'] = ' '.join(details['genre'])
		infoLabels['year'] = details['year']
		infoLabels['country'] = ' '.join(details['country'])

		if 'seasons' in details.keys():
			params = {'id': id, 'handler': 'ListSeasons'}
			name = name + ' [сериал]'		
			torrents = searchDownloads(downloads, id=id)
			if len(torrents) > 0:
				ready = False
				for torrent in torrents:
					if torrent['torrent']['percentDone'] == 1:
						ready=True
						break
				if ready:
					name = util.color(name, 'green')
				else:
					name = util.color(name, 'orange')
		else:
			torrents = searchDownloads(downloads, id=id)
			if len(torrents) == 0:
				params = {'id': id, 'handler': 'AddTorrent'}				
			else:
				download = torrents[0]
				contextCmd = 'RunPlugin(' + _baseUrl+'?' + urllib.urlencode({'handler': 'RemoveTorrent', 'hashString': download['torrent']['hashString']}) + ')'
				contextMenuItems.append(('Remove Torrent',contextCmd))
				if download['torrent']['percentDone'] == 1:
					name = util.color(name, 'green')
					params = {'hashString': download['torrent']['hashString'], 'handler': 'ListTorrentFiles'}		
				else: 
					name = util.color(name, 'orange')
					params = {'hashString': download['torrent']['hashString'], 'handler': 'MonitorTorrent'}

			
		if 'myrating' in details.keys():
			infoLabels['userrating'] = float(details['myrating'])
			infoLabels['playcount'] = 1
		elif 'seasons' not in details.keys():
			contextCmd = 'RunPlugin(' + _baseUrl+'?' + urllib.urlencode({'handler': 'ContentWatched', 'id': id}) + ')'
			contextMenuItems.append(('Watched',contextCmd))
		item = xbmcgui.ListItem(name)	
		item.setCast(details['actors'] + details['directors'])
		item.setArt({'thumb': kinopoisk.getThumb(id), 'poster': kinopoisk.getPoster(id), 'fanart': kinopoisk.getPoster(id)})
		item.setInfo( type="Video", infoLabels=infoLabels )											
		item.addContextMenuItems(contextMenuItems, replaceItems=True)		
		xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?' + urllib.urlencode(params), isFolder=True, listitem=item)
	xbmcplugin.endOfDirectory(_handleId)
	cache.flush(c, _cacheFolder)

	
def handlerListSeasons():
	s = util.Session(_cookiesFolder)
	c = cache.init(_cacheFolder)	
	downloads = transmission.get(s, _transmissionUrl, _transmissionDownloadsFolder)
	details=cache.get(c, _params['id'])
	if 'seasonsWatched' not in details.keys():
		try:
			xbmc.executebuiltin( "ActivateWindow(busydialog)" )
			details['seasonsWatched'] = kinopoiskplus.getSeasons(s, _params['id'])['seasonsWatched']
			cache.set(c, _params['id'], details)
			cache.flush(c, _cacheFolder)
			xbmc.executebuiltin( "Dialog.Close(busydialog)" )
		except:
			exc_type, exc_value, exc_traceback = sys.exc_info()
			log(traceback.format_exc(),xbmc.LOGERROR)	
			xbmc.executebuiltin( "Dialog.Close(busydialog)" )
			xbmcgui.Dialog().ok('Error', 'Error detected while retrieving watched seasons', 'Check log for details')
			return			
	xbmcplugin.setContent(_handleId, 'movies')
	for season in range (1, details['seasons'] + 1):
		name = 'Сезон ' + str(season)
		contextMenuItems = []
		if season <= details['seasonsWatched']:
			infoLabels = {'playCount':1}
		else:
			infoLabels = {'playCount':0}
		if season == details['seasonsWatched'] + 1:
			contextCmd = 'RunPlugin(' + _baseUrl+'?' + urllib.urlencode({'handler': 'SeasonWatched', 'id': _params['id'], 'season': season}) + ')'
			contextMenuItems.append(('Watched',contextCmd))
		
		
		torrents = searchDownloads(downloads, id=_params['id'], season=season)
		if len(torrents) == 0:
			params = {'id': _params['id'], 'season': season, 'handler': 'AddTorrent'}				
		else:
			download = torrents[0]
			contextCmd = 'RunPlugin(' + _baseUrl+'?' + urllib.urlencode({'handler': 'RemoveTorrent', 'hashString': download['torrent']['hashString']}) + ')'
			contextMenuItems.append(('Remove Torrent',contextCmd))
			if download['torrent']['percentDone'] == 1:
				name = util.color(name, 'green')
				params = {'hashString': download['torrent']['hashString'], 'handler': 'ListTorrentFiles'}		
			else: 
				name = util.color(name, 'orange')
				params = {'hashString': download['torrent']['hashString'], 'handler': 'MonitorTorrent'}
				contextCmd = 'RunPlugin(' + _baseUrl+'?' + urllib.urlencode({'handler': 'FilterTorrentFiles', 'id': _params['id'], 'season': season, 'selected':'current', 'hashString': download['torrent']['hashString']}) + ')'
				contextMenuItems.append(('Filter Manual',contextCmd))			
				contextCmd = 'RunPlugin(' + _baseUrl+'?' + urllib.urlencode({'handler': 'FilterTorrentFiles', 'id': _params['id'], 'season': season, 'selected':'unwatched','hashString': download['torrent']['hashString']}) + ')'
				contextMenuItems.append(('Filter Watched',contextCmd))
		
		
		
		
		item = xbmcgui.ListItem(name)			
		item.setInfo( type="Video", infoLabels=infoLabels )											
		item.addContextMenuItems(contextMenuItems, replaceItems=True)		
		xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?' + urllib.urlencode(params), isFolder=True, listitem=item)
	if not details['seasonsFinal']:
		item = xbmcgui.ListItem('~Сезон ' + str(details['seasons'] + 1))			
		infoLabels = {'playCount':0}
		params = {'id': id, 'season': details['seasons'] + 1, 'handler': 'FutureSeason'}
		item.setInfo( type="Video", infoLabels=infoLabels )													
		xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?' + urllib.urlencode(params), isFolder=True, listitem=item)
	xbmcplugin.endOfDirectory(_handleId)
	

def handlerFutureSeason():
	xbmcgui.Dialog().ok('Error', 'Future season')

	
	

	
	
def getTorrentVideoFilesList(torrent):
	result = []
	files = sorted(torrent['files'], key=lambda k: k['name']) 
	for file in files:
		name = util.fileName(file['name'])
		pathOrig = file['name'].replace(name,'')
		path = _transmissionDownloadsFolder + pathOrig
		if util.fileExt(name.lower()) in ['avi','mkv','mp4']:
			item=xbmcgui.ListItem(name)
			item.setPath(path+name)
#			info = xbmcdb.getVideoInfo(name,path)
			info = xbmcdb.getVideoInfo(name, pathOrig)
			item.setInfo( type="Video", infoLabels=info )
			if info is None:
				info = {'playcount':0}
			item.setProperty('code',str({'idFile': file['id'], 'playCount': info['playcount'], 'wanted': file['wanted']}))						
			result.append(item)
	return result
	

def handlerListTorrentFiles():
	torrent = searchDownloads(hashString = _params['hashString'])[0]['torrent']
	xbmcplugin.setContent(_handleId, 'files')
	for item in getTorrentVideoFilesList(torrent):
		d = eval(item.getProperty('code'))
		if d['wanted']:
			xbmcplugin.addDirectoryItem(handle=_handleId, listitem=item, url=item.getPath())
	xbmcplugin.endOfDirectory(_handleId)
	

def handlerFilterTorrentFiles():
	torrent = searchDownloads(hashString=_params['hashString'])[0]['torrent']
	list = getTorrentVideoFilesList(torrent)
	selected = []
	for i in range (0, len(list)):
		d = eval(list[i].getProperty('code'))	
		if _params['selected'] == 'current':			
			if d['wanted']:
				selected.append(i)
		else:
			if not d['playCount'] > 0:
				selected.append(i)		
	result = xbmcgui.Dialog().multiselect("Included files", list, preselect=selected)			
	if result is None:
		return
	unselected = []
	for i in range (0, len(list)):
		if i not in result:
			d = eval(list[i].getProperty('code'))
			unselected.append(d['idFile'])	
	s = util.Session(_cookiesFolder)
	transmission.modify(s, _transmissionUrl, _params['hashString'], {'files-wanted': []})
	if len(unselected) > 0:
		transmission.modify(s, _transmissionUrl, _params['hashString'], {'files-unwanted': unselected})
		
		
def handlerMonitorTorrent():
	w = gui.DialogDownloadStatus("DialogDownloadStatus.xml",_path )	
	w.setData({'function': searchDownloads, 'hashString': _params['hashString']})
	w.doModal()
	w.stop()
	del w
	xbmc.executebuiltin('Container.Refresh')
	
	
def handlerRemoveTorrent():
	s = util.Session(_cookiesFolder)
	transmission.remove(s, _transmissionUrl, _params['hashString'], True, _transmissionDownloadsFolder)
	xbmc.executebuiltin('Container.Refresh')

	
def handlerAddTorrent():	
	s = util.Session(_cookiesFolder)
	downloads = transmission.get(s, _transmissionUrl, _transmissionDownloadsFolder)
	downloads = searchDownloads(downloads, id=_params['id'])

	s = util.Session(_cookiesFolder)	
	rutracker.loginVerify(s, _rutrackerUser, _rutrackerPassword)
	c = cache.init(_cacheFolder)
	details=cache.get(c, _params['id'])
	searchStr = details['name']
#	strictDirectors = []
#	for director in details['directors']:
#		strictDirectors.append(director['name'])
#	strict = [strictDirectors]
	strict = []
	
	if 'season' in _params.keys():
		if details['seasons'] > 1:
			searchStr = searchStr + ' Сезон ' + _params['season']
			strictSeason = ['Сезон: ' + _params['season']]
			strict.append(strictSeason)


#	torrents = rutracker.search(s, searchStr, strict)
	
	torrents = []
	for director in details['directors']:	
		t = rutracker.search(s, searchStr + ' ' + director['name'], strict)
		if len(t)>len(torrents):
			torrents = t
	torrentsFiltered = []
	for torrent in torrents:
		exists = False
		for download in downloads:
			if download['metadata']['torrentName'] == torrent['name']:
				exists = True
				break
		if not exists:
			torrentsFiltered.append(torrent)
	torrents = torrentsFiltered	
	if len(torrents) == 0:
		xbmcgui.Dialog().ok('Error',  'Torrents not found')
		return
	values = []
	for torrent in torrents:				
			values.append ('[' + str(round((float(torrent["size"]) / (1024*1024*1024)),2)) + 'Gb, ' + torrent["seeds"] + ' Seeds] ' + torrent['name'] )
	result = xbmcgui.Dialog().select("Torrents", values)			
	if result==-1:
		return
	torrent = torrents[result]	
	data = {'id': _params['id'], 'torrentName': torrent['name']}
	if 'season' in _params.keys():
		data.update({'season': int(_params['season'])})
	transmission.add(s, _transmissionUrl, torrent['url'], _transmissionDownloadsFolder, data)
	xbmc.executebuiltin('Container.Refresh')
	
	
def log(message,loglevel=xbmc.LOGNOTICE):
	xbmc.log('plugin.video.kinopoisk' + " : " + message,level=loglevel)
		
	
def handlerContentWatched():
	s = util.Session(_cookiesFolder)
	kinopoiskplus.loginVerify(s, _kinopoiskUser, _kinopoiskPassword)
	c = cache.init(_cacheFolder)
	details=cache.get(c, _params['id'])
	values = []
	for i in range(1,10):
		values.append(str(i+1))
	result = xbmcgui.Dialog().select('Оценка', values)
	if not result>=0:
			return					
	try:
		xbmc.executebuiltin( "ActivateWindow(busydialog)" )				
		kinopoisk.setWatched(s, _params['id'], True, values[result])	
		details['myrating'] = int(values[result])
		xbmc.executebuiltin( "Dialog.Close(busydialog)" )
	except:
		exc_type, exc_value, exc_traceback = sys.exc_info()
		log(traceback.format_exc(),xbmc.LOGERROR)	
		xbmc.executebuiltin( "Dialog.Close(busydialog)" )
		xbmcgui.Dialog().ok('Error', 'Error detected while updating rate', 'Check log for details')
		return
	cache.set(c, _params['id'], details)
	cache.flush(c, _cacheFolder)
	xbmc.executebuiltin('Container.Refresh')			

	
def handlerSeasonWatched():
	s = util.Session(_cookiesFolder)
	kinopoiskplus.loginVerify(s, _kinopoiskUser, _kinopoiskPassword)
	c = cache.init(_cacheFolder)
	details=cache.get(c, _params['id'])
	if 'myrating' not in details.keys():
		values = []
		for i in range(1,10):
			values.append(str(i+1))
		result = xbmcgui.Dialog().select('Оценка', values)
		if not result>=0:
			return
		try:
			xbmc.executebuiltin( "ActivateWindow(busydialog)" )				
			kinopoisk.setWatched(s, _params['id'], True, values[result])	
			details['myrating'] = int(values[result])			
			xbmc.executebuiltin( "Dialog.Close(busydialog)" )
		except:
			exc_type, exc_value, exc_traceback = sys.exc_info()
			log(traceback.format_exc(),xbmc.LOGERROR)	
			xbmc.executebuiltin( "Dialog.Close(busydialog)" )
			xbmcgui.Dialog().ok('Error', 'Error detected while updating rate', 'Check log for details')
			return
	try:
		xbmc.executebuiltin( "ActivateWindow(busydialog)" )
		kinopoiskplus.setSeasonWatched(s,_params['id'],_params['season'], True)
		details['seasonsWatched'] = int(_params['season'])		
		xbmc.executebuiltin( "Dialog.Close(busydialog)" )
	except:
		exc_type, exc_value, exc_traceback = sys.exc_info()
		log(traceback.format_exc(),xbmc.LOGERROR)	
		xbmc.executebuiltin( "Dialog.Close(busydialog)" )
		xbmcgui.Dialog().ok('Error', 'Error detected while updating watched seasons', 'Check log for details')	
		return
	cache.set(c, _params['id'], details)
	cache.flush(c, _cacheFolder)
	xbmc.executebuiltin('Container.Refresh')		
	
	


def handlerFolderAdd():	
	s = util.Session(_cookiesFolder)
	kinopoiskplus.loginVerify(s, _kinopoiskUser, _kinopoiskPassword)
	folders = util.fileToObj(_path + '/folders')
	result = xbmcgui.Dialog().select("Select Folder", folders.values())
	if result==-1:
		return		
	try:
		xbmc.executebuiltin( "ActivateWindow(busydialog)" )
		kinopoisk.assignToFolder(s, _params['id'], folders.keys()[result], True)	
		xbmc.executebuiltin( "Dialog.Close(busydialog)" )
	except:
		exc_type, exc_value, exc_traceback = sys.exc_info()
		log(traceback.format_exc(),xbmc.LOGERROR)	
		xbmc.executebuiltin( "Dialog.Close(busydialog)" )
		xbmcgui.Dialog().ok('Error', 'Error detected while adding to folder', 'Check log for details')
	
	
def handlerFolderRemove():	
	s = util.Session(_cookiesFolder)
	kinopoiskplus.loginVerify(s, _kinopoiskUser, _kinopoiskPassword)
	try:
		xbmc.executebuiltin( "ActivateWindow(busydialog)" )
		kinopoisk.assignToFolder(s, _params['id'], _params['folder'], False)
		xbmc.executebuiltin( "Dialog.Close(busydialog)" )
		xbmc.executebuiltin('Container.Refresh')
	except:
		exc_type, exc_value, exc_traceback = sys.exc_info()
		log(traceback.format_exc(),xbmc.LOGERROR)	
		xbmc.executebuiltin( "Dialog.Close(busydialog)" )
		xbmcgui.Dialog().ok('Error', 'Error detected while removing from folder', 'Check log for details')
	
	
def handlerFolderMove():	
	s = util.Session(_cookiesFolder)
	kinopoiskplus.loginVerify(s, _kinopoiskUser, _kinopoiskPassword)
	folders = util.fileToObj(_path + '/folders')
	del folders[_params['folder']]
	result = xbmcgui.Dialog().select("Select Folder", folders.values())
	if result==-1:
		return		
	try:
		xbmc.executebuiltin( "ActivateWindow(busydialog)" )
		kinopoisk.assignToFolder(s, _params['id'], _params['folder'], False)
		kinopoisk.assignToFolder(s, _params['id'], folders.keys()[result], True)	
		xbmc.executebuiltin( "Dialog.Close(busydialog)" )
		xbmc.executebuiltin('Container.Refresh')
	except:
		exc_type, exc_value, exc_traceback = sys.exc_info()
		log(traceback.format_exc(),xbmc.LOGERROR)	
		xbmc.executebuiltin( "Dialog.Close(busydialog)" )
		xbmcgui.Dialog().ok('Error', 'Error detected while moving folder', 'Check log for details')
	
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
	s = util.Session(_cookiesFolder)
	kinopoiskplus.loginVerify(s, _kinopoiskUser, _kinopoiskPassword)		
	if result['name'] is not None:
		content = kinopoisk.searchByTitle(s, title = result['name'], contentType=result['action'])
	else:			
		content = kinopoisk.searchByParams(s, contentType=result['action'], hideWatched=True, hideInFolders=True, genre=result['genres'], years=result['years'], countries=result['countries'])			
	params = {
		'handler': 'SearchResults',
		'content': str(content)
	}
	url=_baseUrl+'?' + urllib.urlencode( params )	
	xbmc.executebuiltin("Container.Update(" + url + ")")
	
	
	


def handlerInfo():	
	xbmc.executebuiltin('Action(info)')


def handlerListFolder():
	s = util.Session(_cookiesFolder)
	kinopoiskplus.loginVerify(s, _kinopoiskUser, _kinopoiskPassword)
	content = kinopoisk.getFolderContent(s, _params['folder'])
	listContent(content, _params['folder'])
	

def handlerDownloads():
	content = []
	s = util.Session(_cookiesFolder)
	downloads = transmission.get(s, _transmissionUrl, _transmissionDownloadsFolder)
	for download in downloads:
		if 'metadata' in download.keys():
			exists = False
			for id in content:
				if id == download['metadata']['id']:
					exists = True
			if not exists:
				content.append(download['metadata']['id'])
	listContent(content)

	
def handlerRoot():	
	
#	c = cache.init(_cacheFolder)
#	cache.purge(c, _cacheAge)
#	cache.flush(c, _cacheFolder)
	
	
	pathImg = _path + '/resources/img/'	
	rootLinks = [
		{'name': 'Search', 'urlParams': {'handler': 'Search'}, 'icon': pathImg+'Search.png'},
		{'name': 'Downloads', 'urlParams': {'handler': 'Downloads'}, 'icon': pathImg+'Downloads.png'}
	]
	s = util.Session(_cookiesFolder)
	kinopoiskplus.loginVerify(s, _kinopoiskUser, _kinopoiskPassword)
	folders = kinopoisk.getFolders(s)
	util.objToFile(folders, _path + '/folders')
	for id in folders.keys():
		icon = pathImg + folders[id] + '.png'
		if not xbmcvfs.exists(icon):
			icon = None
		rootLinks.append({
			'name': folders[id],
			'urlParams': {'handler': 'ListFolder', 'folder': id},
			'icon': icon
		})
	for rootLink in rootLinks:
		item=xbmcgui.ListItem(rootLink['name'], iconImage=rootLink['icon'])		
		xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?'+urllib.urlencode(rootLink['urlParams']), isFolder=True, listitem=item)
	xbmcplugin.endOfDirectory(_handleId)


	
if 'handler' in _params.keys():
	globals()['handler' + _params['handler']]()
else:
	handlerRoot()
	

#	download['torrent']['percentDone'] == 1:
	
	
