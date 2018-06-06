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
_folders = _dataFolder + '/folders'
_downloads = _dataFolder + '/downloads'



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


	
def listContent(content, folder='0'):
	xbmcplugin.setContent(_handleId, 'movies')
	for item in content:		
		contextMenuItems = []
		contextCmd = 'RunPlugin(' + _baseUrl+'?' + urllib.urlencode({'handler': 'Info', 'item': item}) + ')'
		contextMenuItems.append(('Информация',contextCmd))		
		name = item['title']
		if item['type'] == 'SHOW':
			name = name + ' (сериал)'
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
		else:
			infoLabels['playCount'] = 0
		contextCmd = 'RunPlugin(' + _baseUrl+'?' + urllib.urlencode({'handler': 'WatchedAll', 'item': item}) + ')'
		contextMenuItems.append(('Посмотрел',contextCmd))			
		infoLabels['plot'] = plot
		li = xbmcgui.ListItem(name)	
		li.setArt({'thumb': kinopoiskplus.getThumb(item['id']), 'poster': kinopoiskplus.getPoster(item['id']), 'fanart': kinopoiskplus.getPoster(item['id'])})
		li.setInfo( type="Video", infoLabels=infoLabels )											
		li.addContextMenuItems(contextMenuItems, replaceItems=True)		
		params = {'item': item, 'handler': 'ListTorrents'}
		xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?' + urllib.urlencode(params), isFolder=True, listitem=li)
	xbmcplugin.endOfDirectory(_handleId)


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
			contextCmd = 'RunPlugin(' + _baseUrl+'?' + urllib.urlencode({'handler': 'Watched', 'item': _params['hashString'] + '|' + name, 'watched': 'false'}) + ')'
			contextMenuItems.append(('UnWatched',contextCmd))
		else:
			infoLabels['playcount'] = 0
			contextCmd = 'RunPlugin(' + _baseUrl+'?' + urllib.urlencode({'handler': 'Watched', 'item': _params['hashString'] + '|' + name, 'watched': 'true'}) + ')'
			contextMenuItems.append(('Watched',contextCmd))
		item=xbmcgui.ListItem(name, iconImage=_pathImg + 'video.png')
		item.addContextMenuItems(contextMenuItems, replaceItems=True)	
		item.setInfo( type="Video", infoLabels=infoLabels )	
		params = {
			'handler': 'Play',
			'url': url,
			'name': name,
			'hashString': _params['hashString'],
			'item': _params['item']
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
	item = eval(_params['item'])	
	torrents = []	
	directors = kinopoiskplus.getCast(_cookiesKinopoisk, item['id'],'director')
	downloads = getDownloads()
	dtorrents = []
	if item['id'] in downloads.keys():
		dtorrents = downloads[item['id']]['torrents'].values()
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
	if item['id'] not in downloads.keys():
		downloads.update({item['id']: {'torrents': {} } })
	downloads[item['id']]['torrents'][hashString] = torrent['name']
	setDownloads(downloads)
	kinopoiskplus.setFolder(_cookiesKinopoisk, item['id'], getFolder('Смотрю'), True)
	kinopoiskplus.setFolder(_cookiesKinopoisk, item['id'], getFolder('Буду Смотреть'), False)	
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
	item = eval(_params['item'])
	downloads = getDownloads()
	content = []
	torrents = {}
	if item['id'] in downloads.keys():
		torrents = downloads[item['id']]['torrents']
	for hashString, name in torrents.iteritems():					
		contextMenuItems = []
		data = transmission.get(_transmissionUrl, [hashString])[0]
		if data['percentDone'] == 1:
			params = {
				'handler': 'ListTorrent',
				'hashString': hashString,
				'torrentName': name,
				'item': _params['item']
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
		contextCmd = 'RunPlugin(' + _baseUrl+'?' + urllib.urlencode({'handler': 'RemoveTorrent', 'id': item['id'], 'hashString': hashString}) + ')'
		contextMenuItems.append(('Remove',contextCmd))	
		li=xbmcgui.ListItem(name, iconImage=_pathImg + 'torrent.png')
		li.addContextMenuItems(contextMenuItems, replaceItems=True)						
		xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?'+urllib.urlencode(params), isFolder=True, listitem=li)
	li=xbmcgui.ListItem('Add Torrent', iconImage=_pathImg + 'addtorrent.png')		
	params = {'handler': 'AddTorrent', 'item': _params['item']}
	xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?'+urllib.urlencode(params), isFolder=True, listitem=li)
	xbmcplugin.endOfDirectory(_handleId)


	
def handlerWatchedAll():
	item = eval(_params['item'])	
	kinopoiskplus.setFolder(_cookiesKinopoisk, item['id'], getFolder('Смотрю'), False)
	if not item['watched']:
		kinopoiskplus.setWatched(_cookiesKinopoisk, item['id'], True, item['usercode'])
	downloads = getDownloads()
	if item['id'] in downloads.keys():
		for hashString in downloads[item['id']]['torrents'].keys():
			transmission.remove(_transmissionUrl, hashString, True)
	del downloads[item['id']]
	setDownloads(downloads)	
	xbmc.executebuiltin('Container.Refresh')	
	
	
def handlerWatched():		
	if _params['watched'] == 'true':
		watchlog.setWatched(_watchedFolder, _baseUrl, _params['item'])
	else:
		watchlog.setUnWatched(_watchedFolder,_baseUrl, _params['item'])
	xbmc.executebuiltin("Container.Refresh()")


def handlerInfo():
	item = eval(_params['item'])
	title = item['title']
	if item['originalTitle'] is not None:
		title = title + ' / ' + item['originalTitle']
	details = kinopoiskplus.getDetails(_cookiesKinopoisk, item['id'])
	if item['type'] == 'SHOW':
		if 'seasons' in details.keys():
			title = title + ' (сезоны: ' + str(details['seasons']) + ')'
		else:
			title = title + ' (сезоны: 1)'
	infoLabels = {}
	infoLabels['plot'] = details['description']
	li = xbmcgui.ListItem(title)	
	li.setArt({'thumb': kinopoiskplus.getThumb(item['id']), 'poster': kinopoiskplus.getPoster(item['id']), 'fanart': kinopoiskplus.getPoster(item['id'])})
	li.setInfo( type="Video", infoLabels=infoLabels )		
	li.setCast(kinopoiskplus.getCast(_cookiesKinopoisk, item['id'],'actor'))
	dialog = xbmcgui.Dialog()
	ret = dialog.info(li)	


#def handlerRecommendationResult():	
#	content = kinopoiskplus.getRecommended(_cookiesKinopoisk, eval(_params['criteria']))
#	listContent(content)
	
	
#def handlerRecommendation():
#	criteria = []
#	filters = kinopoiskplus.getRecommendedCriteria(_cookiesKinopoisk)
#	for filter in filters:
#		if filter['multiple']:
#			selected = xbmcgui.Dialog().multiselect(filter['displayName'], filter['values'], preselect=[])
#			if selected:
#				values = []
#				for i in selected:
#					values.append(filter['values'][i])
#				criteria.append({'param': filter['param'], 'values': values})	
#		else:
#			selected = xbmcgui.Dialog().select(filter['displayName'], filter['values'])			
#			if selected != -1:
#				criteria.append({'param': filter['param'], 'values': [filter['values'][selected]]})	
#	params = {
#		'handler': 'RecommendationResult',
#		'criteria': criteria
#	}
#	url=_baseUrl+'?' + urllib.urlencode( params )	
#	xbmc.executebuiltin("Container.Update(" + url + ")")


	
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
	if not os.path.isfile(_downloads):
		return {}
	downloads = util.fileToObj(_downloads)	
	hashStrings = []
	data = transmission.get(_transmissionUrl)
	for row in data:
		hashStrings.append(row['hashString'])
	changed = False
	for id in downloads.keys():
		for hashString in downloads[id]['torrents'].keys():
			if hashString not in hashStrings:
				del downloads[id]['torrents'][hashString]
				changed = True
		if not downloads[id]['torrents']:
			del downloads[id]
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
	

	
def handlerListFolder():
	content = kinopoiskplus.getFolderContent(_cookiesKinopoisk, _params['folder'])
	listContent(content, _params['folder'])
	
	

def loginKinopoisk():
	if os.path.isfile(_cookiesKinopoisk):
		return
	kinopoiskplus.login(_cookiesKinopoisk, _kinopoiskUser, _kinopoiskPassword)

def loginRutracker():
	if os.path.isfile(_cookiesRutracker):
		return
	rutracker.login(_cookiesRutracker, _rutrackerUser, _rutrackerPassword)
	
def getFolder(name):
	folders = util.fileToObj(_folders)
	return folders.get(name,'None')
	
	
def handlerRoot():	
	loginKinopoisk()
	loginRutracker()
	folders = kinopoiskplus.getFolders(_cookiesKinopoisk)
	util.objToFile(folders,_folders)	
	for name, id in folders.iteritems():
		params = {
			'handler': 'ListFolder',
			'folder': id
		}
		item=xbmcgui.ListItem(name, iconImage=_pathImg + 'Folder.png')
		xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?'+urllib.urlencode(params), isFolder=True, listitem=item)
	rootLinks = [		
		{'name': 'Поиск', 'urlParams': {'handler': 'Search'}, 'icon': _pathImg+'Search.png'}
#		{'name': 'Рекоммендация', 'urlParams': {'handler': 'Recommendation'}, 'icon': _pathImg+'Recommendation.png'}
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
