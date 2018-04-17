# coding: utf-8

import sys
import os
import urlparse
import xbmc
import xbmcgui
import xbmcplugin
import urllib
import urllib2
import xbmcaddon
import util



_baseUrl = sys.argv[0]
_handleId = int(sys.argv[1])
_params = dict(urlparse.parse_qsl(sys.argv[2][1:], keep_blank_values=True))	
_addon = xbmcaddon.Addon()
_path = _addon.getAddonInfo('path') + '/'


_dataFolder = _addon.getSetting('dataFolder')



reload(sys)  
sys.setdefaultencoding('utf8')	


def validateSettings():
	if len(_dataFolder)==0: 
		xbmcgui.Dialog().ok('Error', 'Please configure settings')
		return False
	return True


	
def handlerListPath():
	autoplay = []
	autoplayIndex = 0
	pathImg = _path + '/resources/img/'	
	files = []
	dirs = []
	for f in os.listdir(_params['path']):
		path = os.path.join(_params['path'],f)
		if os.path.isfile(path):			
			if util.fileExt(path.lower()) in ['avi','mkv','mp4']:						
				files.append({'name': f, 'path': path})
		else:
			dirs.append({'name': f, 'path': path})
	for f in dirs:
		item=xbmcgui.ListItem(f['name'])
		params = {
			'handler': 'ListPath',
			'path': f['path']
		}
		xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?' + urllib.urlencode(params), isFolder=True, listitem=item)				      
	for f in files:
		contextMenuItems=[]
		contextCmd = 'RunPlugin(' + _baseUrl+'?' + urllib.urlencode({'handler': 'AutoPlay', 'autoplayIndex': str(autoplayIndex)}) + ')'
		contextMenuItems.append(('Auto Play',contextCmd))
		item=xbmcgui.ListItem(f['name'], iconImage=pathImg+'video.png')
		item.addContextMenuItems(contextMenuItems, replaceItems=True)
		params = {
			'handler': 'Play',
			'path': f['path'],
			'name': f['name']
		}
		xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?' + urllib.urlencode(params), isFolder=True, listitem=item)
		autoplay.append(params)
		autoplayIndex = autoplayIndex + 1
	xbmcplugin.endOfDirectory(_handleId)
	util.objToFile(autoplay, _path + '/autoplay')

		
		
def handlerAddPath():
	path = xbmcgui.Dialog().browseSingle(0, 'Choose Media Location','videos')
	if len(path) == 0:
		return
	kb = xbmc.Keyboard('', 'Media Location Name', True)
	kb.setHiddenInput(False)
	kb.doModal()
	name = None
	if kb.isConfirmed():
		name = kb.getText()
	del kb
	if name is None:
		return
	library = getLibrary()
	library.append({'name': name, 'path': path})
	setLibrary(library)
	xbmc.executebuiltin('Container.Refresh')


def handlerRemovePath():
	library = getLibrary()
	del library[int(_params['index'])]
	setLibrary(library)
	xbmc.executebuiltin('Container.Refresh')
	
	
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
	url = 'file:' + urllib.pathname2url(_params['path'])
	util.play(url,_params['name'])
	
	

	
	

	

def getLibrary():
	path = _dataFolder + '/library'
	if not os.path.isfile(path):
		return []
	return util.fileToObj(path)

def setLibrary(library):
	path = _dataFolder + '/library'
	util.objToFile(library, path)
	
	
def handlerRoot():	
	library = getLibrary()
	pathImg = _path + '/resources/img/'	
	for i in range (0, len(library)):
		contextMenuItems = []
		contextCmd = 'RunPlugin(' + _baseUrl+'?' + urllib.urlencode({'handler': 'RemovePath', 'index': i}) + ')'
		contextMenuItems.append(('Remove',contextCmd))		
		item=xbmcgui.ListItem(library[i]['name'])
		item.addContextMenuItems(contextMenuItems, replaceItems=True)		
		params = {'handler': 'ListPath', 'path': library[i]['path']}
		xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?'+urllib.urlencode(params), isFolder=True, listitem=item)
	item=xbmcgui.ListItem('Add Media' , iconImage=pathImg+'add.png')
	xbmcplugin.addDirectoryItem(handle=_handleId, url=_baseUrl+'?'+urllib.urlencode({'handler': 'AddPath'}), isFolder=True, listitem=item)
	xbmcplugin.endOfDirectory(_handleId)


if validateSettings():
	if 'handler' in _params.keys():
		globals()['handler' + _params['handler']]()
	else:
		handlerRoot()
