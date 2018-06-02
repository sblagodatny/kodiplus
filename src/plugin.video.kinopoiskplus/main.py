# coding: utf-8

import sys
import os
import urlparse
import xbmc
import xbmcgui
import xbmcplugin
import urllib
import urllib2
import kinopoiskplus
import rutracker
import transmission
import xbmcaddon
import util
import gui
import time
import watchlog
import datetime


_baseUrl = sys.argv[0]
_handleId = int(sys.argv[1])
_params = dict(urlparse.parse_qsl(sys.argv[2][1:], keep_blank_values=True))	
_addon = xbmcaddon.Addon()
_path = _addon.getAddonInfo('path') + '/'
_pathImg = _path + '/resources/img/'	


_dataFolder = _addon.getSetting('dataFolder')
_kinopoiskUser = _addon.getSetting('kinopoiskUser')
_kinopoiskPassword = _addon.getSetting('kinopoiskPassword')
_rutrackerUser = _addon.getSetting('rutrackerUser')
_rutrackerPassword = _addon.getSetting('rutrackerPassword')
_transmissionUrl = _addon.getSetting('transmissionUrl')
_transmissionDownloadsFolder = _addon.getSetting('transmissionDownloadsFolder')
_watchedFolder = _addon.getSetting('watchedFolder')

_cookiesKinopoisk = _dataFolder + '/cookiesKinopoisk'
_cookiesRutracker = _dataFolder + '/cookiesRutracker'

_refreshFlag = _path + '/refresh'


reload(sys)  
sys.setdefaultencoding('utf8')	


_mandatorySettings = [
	'dataFolder', 
	'kinopoiskUser', 
	'kinopoiskPassword', 
	'rutrackerUser', 
	'rutrackerPassword', 
	'transmissionUrl',
	'transmissionDownloadsFolder',
	'watchedFolder'
]	



def validateSettings():
	for setting in _mandatorySettings:
		if len(_addon.getSetting(setting))==0:
			xbmcgui.Dialog().ok('Error', 'Please configure settings')
			return False
	return True


	
def listContent(content, folder=-1):
	cache = {}
	xbmcplugin.setContent(_handleId, 'movies')
	for item in content:		
		contextMenuItems = []
		contextCmd = 'RunPlugin(' + _baseUrl+'?' + urllib.urlencode({'handler': 'Info', 'id': item['id']}) + ')'
		contextMenuItems.append(('Информация',contextCmd))		
		name = item['title']
		if item['type'] == 'SHOW':
			name = name + ' (сериал)'
			contextCmd = 'RunPlugin(' + _baseUrl+'?' + urllib.urlencode({'handler': 'Seasons', 'id': item['id']}) + ')'
			contextMenuItems.append(('Сезоны',contextCmd))		
		infoLabels = {}	
		plot = ''
		if item['originalTitle'] is not None:
			plot = plot + util.bold(item['originalTitle']) + "\n"
		plot = plot + '________________' + "\n\n\n\n"
		plot = plot + util.bold('Рейтинг: ') + item['rate'] + "\n\n" 
		plot = plot + util.bold('Год: ') + item['year'] + "\n\n"
		plot = plot + util.bold('Жанр: ') + item['genres'] + "\n\n"
		plot = plot + util.bold('Страна: ') + item['countries'] + "\n\n"
		if item['watched']:
			infoLabels['playcount'] = 1
			contextCmd = 'RunPlugin(' + _baseUrl+'?' + urllib.urlencode({'handler': 'SetWatchedKinopoisk', 'id': item['id'], 'watched': 'False'}) + ')'
			contextMenuItems.append(('UnWatched',contextCmd))
		else:
			infoLabels['playCount'] = 0
			contextCmd = 'RunPlugin(' + _baseUrl+'?' + urllib.urlencode({'handler': 'SetWatchedKinopoisk', 'id': item['id'], 'watched': 'True'}) + ')'
			contextMenuItems.append(('Watched',contextCmd))		
		infoLabels['plot'] = plot
		li = xbmcgui.ListItem(name)	
		li.setArt({'thumb': kinopoiskplus.getThumb(item['id']), 'poster': kinopoiskplus.getPoster(item['id']), 'fanart': kinopoiskplus.getPoster(item['id'])})
		li.setInfo( type="Video", infoLabels=infoLabels )											
		li.addContextMenuItems(contextMenuItems, replaceItems=True)		
		params = {'id': item['id'], 'handler': 'ListTorrents'}
		xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?' + urllib.urlencode(params), isFolder=True, listitem=li)
		cache.update({item['id']: item})
	xbmcplugin.endOfDirectory(_handleId)
	util.objToFile(cache, _path + '/cache')
	




def handlerFilterTorrent():
	watchlog.init(_watchedFolder,_path)	
	data = transmission.get(_transmissionUrl, _params['hashString'])[0]
	files = sorted(data['files'], key=lambda k: k['name']) 
	fileslist = []
	selected = []
	for i in range(0,len(files)):
		name = files[i]['name']
		if watchlog.isWatched(_watchedFolder, _baseUrl, _params['hashString'] + '|' + name):
			name = 'V ' + name
		fileslist.append(xbmcgui.ListItem(name))
		if files[i]['wanted']:
			selected.append(i)
	selected = xbmcgui.Dialog().multiselect("Folders", fileslist, preselect=selected)			
	if selected is None:
		return	
	unselected = []
	for i in range(0,len(files)):
		if i not in selected:
			unselected.append(files[i]['id'])
	transmission.modify(_transmissionUrl, _params['hashString'], {'files-wanted': []})
	if len(unselected) > 0:
		transmission.modify(_transmissionUrl, _params['hashString'], {'files-unwanted': unselected})
	
	
def handlerListTorrent():
	xbmcplugin.setContent(_handleId, 'movies')
	autoplay = []
	autoplayIndex = 0
	pathImg = _path + '/resources/img/'	
	watchlog.init(_watchedFolder,_path)	
	data = transmission.get(_transmissionUrl, _params['hashString'])[0]
	files = sorted(data['files'], key=lambda k: k['name']) 
	for file in files:
		if not file['wanted']:
			continue
		contextMenuItems=[]
		contextCmd = 'RunPlugin(' + _baseUrl+'?' + urllib.urlencode({'handler': 'AutoPlay', 'autoplayIndex': str(autoplayIndex)}) + ')'
		contextMenuItems.append(('Auto Play',contextCmd))
		path = os.path.abspath(_transmissionDownloadsFolder + file['name']).encode('utf8')
		url = 'file:' + urllib.pathname2url(path)
#		url = urllib.quote(path.replace("\\",'/'))
		name = util.fileName(urllib.unquote(url))		
		if util.fileExt(path.lower()) not in ['avi','mkv','mp4']:
			continue
		infoLabels = {}
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
		autoplay.append(params)
		autoplayIndex = autoplayIndex + 1
		xbmcplugin.addDirectoryItem(handle=_handleId, url=url, isFolder=True, listitem=item)
	xbmcplugin.endOfDirectory(_handleId)
	util.objToFile(autoplay, _path + '/autoplay')
	

def handlerAutoPlay():		
	autoplayIndex = int(_params['autoplayIndex'])
	autoplay = util.fileToObj(_path + '/autoplay')
	for i in range(autoplayIndex, len(autoplay)):
		_params.update(autoplay[i])
		handlerPlay()
		if i < len(autoplay)-1:
			if xbmcgui.Dialog().yesno(heading='Playing next', line1=' ', line3=autoplay[i+1]['name'], yeslabel='Stop', nolabel='Play', autoclose=8000):
				break
				
	
def handlerPlay():
	watchlog.setWatched(_watchedFolder, _baseUrl, _params['hashString'] + '|' + _params['name'])
	util.play(_params['url'], _params['name'])
	xbmc.executebuiltin("Container.Refresh()")
	
	
	
def handlerAddTorrent():
	cache =	util.fileToObj(_path + '/cache')
	item = cache[_params['id']]
	torrents = []	
	directors = kinopoiskplus.getCast(_cookiesKinopoisk, _params['id'], 'Режиссеры')
	downloads = getDownloads()
	dtorrents = []
	if _params['id'] in downloads.keys():
		dtorrents = downloads[_params['id']]['torrents'].values()
	
	if directors:
		for i in range(0, len(directors)):
			torrentsI = rutracker.search(_cookiesRutracker, item['title'] + ' ' + directors[i]['name'])
			torrents.extend(t for t in torrentsI if t not in torrents and t['name'] not in dtorrents)
			if i==4:
				break
	else:
		torrentsI = rutracker.search(_cookiesRutracker, item['title'])
		torrents.extend(t for t in torrentsI if t not in torrents and t['name'] not in dtorrents)
	
	values = []
	for torrent in torrents:						
		values.append ('[' + str(round((float(torrent["size"]) / (1024*1024*1024)),2)) + 'Gb, ' + torrent["seeds"] + ' Seeds] ' + torrent['name'] )
	result = xbmcgui.Dialog().select("Torrents", values)			
	if result==-1:
		return
	torrent = torrents[result]	
	hashString = transmission.add(_transmissionUrl, torrent['url'], _cookiesRutracker)
	if _params['id'] not in downloads.keys():
		downloads.update({_params['id']: {'item': item, 'torrents': {} } })
	downloads[_params['id']]['torrents'][hashString] = torrent['name']
	setDownloads(downloads)
	xbmc.executebuiltin('Container.Refresh')
	
	
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
	xbmc.executebuiltin('Container.Refresh')
	
	
def handlerListTorrents():
	downloads = getDownloads()
	pathImg = _path + '/resources/img/'	
	content = []
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
	params = {'handler': 'AddTorrent', 'id': _params['id']}
	xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?'+urllib.urlencode(params), isFolder=True, listitem=item)
	xbmcplugin.endOfDirectory(_handleId)

	

def handlerSetFavorites():
	kinopoiskplus.setFavorites(_cookiesKinopoisk, _params['id'], eval(_params['favorite']))
	updateDownloads(_params['id'],{'favorite': eval(_params['favorite'])})
	xbmc.executebuiltin('Container.Refresh')

	
def handlerSetWatchedKinopoisk():
	kinopoiskplus.setWatched(_cookiesKinopoisk, _params['id'], eval(_params['watched']))
	if eval(_params['watched']):
		watched = str(datetime.datetime.today())
		updateDownloads(_params['id'],{'watched': str(datetime.datetime.today())[0:10], 'favorite': False})
	else:
		updateDownloads(_params['id'],{'watched': None})
	xbmc.executebuiltin('Container.Refresh')	
	
	
def handlerSetWatched():		
	if _params['watched'] == 'true':
		watchlog.setWatched(_watchedFolder, _baseUrl, _params['item'])
	else:
		watchlog.setUnWatched(_watchedFolder,_baseUrl, _params['item'])
	xbmc.executebuiltin("Container.Refresh()")


def handlerInfo():
	cache =	util.fileToObj(_path + '/cache')
	item = cache[_params['id']]
	title = item['title']
	if item['originalTitle'] is not None:
		title = title + ' / ' + item['originalTitle']
	details = kinopoiskplus.getDetails(_cookiesKinopoisk, _params['id'])
	infoLabels = {}
	infoLabels['plot'] = details['description']
	li = xbmcgui.ListItem(title)	
	li.setArt({'thumb': kinopoiskplus.getThumb(_params['id']), 'poster': kinopoiskplus.getPoster(_params['id']), 'fanart': kinopoiskplus.getPoster(_params['id'])})
	li.setInfo( type="Video", infoLabels=infoLabels )		
#	li.setCast(
#		kinopoiskplus.getCast(_cookiesKinopoisk, _params['id'], 'Актеры') + 
#		kinopoiskplus.getCast(_cookiesKinopoisk, _params['id'], 'Режиссеры')
#	)
	dialog = xbmcgui.Dialog()
	ret = dialog.info(li)

	
def handlerSeasons():
	data = kinopoiskplus.getSeasons(_cookiesKinopoisk, _params['id'])
	seasons = sorted(data.keys())
	values = []
	selected = []
	for i in range(0, len(seasons)):
		values.append('Сезон ' + str(seasons[i]))
		if data[seasons[i]]:
			selected.append(i)
	selectedNew = xbmcgui.Dialog().multiselect("Просмотренные Сезоны", values, preselect=selected)
	if selectedNew is None:
		return	
	xbmc.executebuiltin( "ActivateWindow(busydialog)" )
	for i in selectedNew:
		if i not in selected:
			kinopoiskplus.setSeasonWatched(_cookiesKinopoisk, _params['id'], seasons[i], True)
	for i in selected:
		if i not in selectedNew:
			kinopoiskplus.setSeasonWatched(_cookiesKinopoisk, _params['id'], seasons[i], False)		
	xbmc.executebuiltin( "Dialog.Close(busydialog)" )
	


def handlerRecommendationResult():	
	content = kinopoiskplus.getRecommended(_cookiesKinopoisk, eval(_params['criteria']))
	listContent(content)
	
	
def handlerRecommendation():
	criteria = []
	filters = kinopoiskplus.getRecommendedCriteria(_cookiesKinopoisk)
	for filter in filters:
		if filter['multiple']:
			selected = xbmcgui.Dialog().multiselect(filter['displayName'], filter['values'], preselect=[])
			if selected:
				values = []
				for i in selected:
					values.append(filter['values'][i])
				criteria.append({'param': filter['param'], 'values': values})	
		else:
			selected = xbmcgui.Dialog().select(filter['displayName'], filter['values'])			
			if selected != -1:
				criteria.append({'param': filter['param'], 'values': [filter['values'][selected]]})	
	params = {
		'handler': 'RecommendationResult',
		'criteria': criteria
	}
	url=_baseUrl+'?' + urllib.urlencode( params )	
	xbmc.executebuiltin("Container.Update(" + url + ")")


	
def handlerSearchResults():	
	content = kinopoiskplus.searchByTitle(_cookiesKinopoisk, _params['searchStr'],_params['type'])
	listContent(content)
	
	
def handlerSearch():		
	type = xbmcgui.Dialog().select('Что искать', ['Фильмы','Сериалы'])
	if type == 0:
		type = 'MOVIE'
	elif type == 1:
		type = 'SHOW'
	else:
		return
	kb = xbmc.Keyboard('', 'Название', True)
	kb.setHiddenInput(False)
	kb.doModal()
	searchStr = None
	if kb.isConfirmed():
		searchStr = kb.getText()
	del kb
	if searchStr is None:
		return
	params = {
		'handler': 'SearchResults',
		'searchStr': searchStr,
		'type': type
	}
	url=_baseUrl+'?' + urllib.urlencode( params )	
	xbmc.executebuiltin("Container.Update(" + url + ")")

			
	
def getDownloads():
	path = _dataFolder + '/downloads'
	if not os.path.isfile(path):
		return {}
	downloads = util.fileToObj(path)	
	hashStrings = []
	data = transmission.get(_transmissionUrl)
	for row in data:
		hashStrings.append(row['hashString'])
	changed = False
	for download in downloads.values():
		for hashString in download['torrents'].keys():
			if hashString not in hashStrings:
				del downloads[download['item']['id']]['torrents'][hashString]
				changed = True
		if not downloads[download['item']['id']]['torrents']:
			del downloads[download['item']['id']]
	if changed:
		setDownloads(downloads)
	return downloads
	

def setDownloads(downloads):
	path = _dataFolder + '/downloads'
	util.objToFile(downloads, path)
	
def updateDownloads(id, data):
	downloads = getDownloads()
	if id not in downloads.keys():
		return
	downloads[id]['item'].update(data)
	setDownloads(downloads)
	
	
def handlerDownloads():
	content = []
	downloads = getDownloads()
	for id, data in downloads.iteritems():
		content.append(data['item'])
	listContent(content)

def handlerFolders():
	folders = kinopoiskplus.getFolders(_cookiesKinopoisk)
	for id, name in folders.iteritems():
		params = {
			'handler': 'ListFolder',
			'folder': id
		}
		item=xbmcgui.ListItem(name, iconImage=_pathImg + 'Folder.png')
		xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?'+urllib.urlencode(params), isFolder=True, listitem=item)
	xbmcplugin.endOfDirectory(_handleId)
	
def handlerListFolder():
	content = kinopoiskplus.getFolderContent(_cookiesKinopoisk, _params['folder'])
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
		{'name': 'Загрузки', 'urlParams': {'handler': 'Downloads'}, 'icon': pathImg+'Downloads.png'},
		{'name': 'Избранное', 'urlParams': {'handler': 'Folders'}, 'icon': pathImg+'Folders.png'},
#		{'name': 'Поиск', 'urlParams': {'handler': 'Search'}, 'icon': pathImg+'Search.png'},
#		{'name': 'Рекоммендация', 'urlParams': {'handler': 'Recommendation'}, 'icon': pathImg+'Recommendation.png'}
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
