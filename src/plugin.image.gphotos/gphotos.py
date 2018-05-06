# coding: utf-8

from bs4 import BeautifulSoup
import requests
import util
import json
import datetime
import google

	
def initSession(pathCookies):
	session = requests.Session()
	session.verify = False
	util.loadCookies(session, pathCookies)
	util.setUserAgent(session, 'chrome')
	return session
	
	
def getMyAlbums(pathCookies):
	session = initSession(pathCookies)
	loginInfo = google.getLoginInfo(session)
	result = []
	content = session.get("https://photos.google.com/albums").text
	dummy, i = util.substr ("key: 'ds:2', isError:  false , hash:","return",content)
	data = json.loads(util.parseBrackets(content, i, ['[',']']))
	for row in data[0]:
		metadata = row[12]['72930366'] ## ==9
		sharedKey =  metadata[5]
		if sharedKey is not None:	
			if len(metadata)!=9:
				continue
		result.append({
			'id': row[0],
			'sharedKey': sharedKey,
			'name': metadata[1],
			'thumb': row[1][0],
			'tsStart': datetime.datetime.fromtimestamp(metadata[2][0]/1000),
			'tsEnd': datetime.datetime.fromtimestamp(metadata[2][1]/1000),
			'owner': loginInfo['name'], 
			'ownerFlag': True,
			'photosCount': metadata[3],			
		})	
#	resultsorted = sorted(result, key=lambda k: k['name'], reverse=True) 	
	return(result)
	
def getOtherAlbums(pathCookies):
	session = initSession(pathCookies)
	loginInfo = google.getLoginInfo(session)
	result = []
	content = session.get("https://photos.google.com/sharing").text
	dummy, i = util.substr ("key: 'ds:1'","return",content)
	data = json.loads(util.parseBrackets(content, i, ['[',']']))
	util.objToFile(str(data[0][0]), pathCookies.replace('/cookies','/data.txt'))
	for row in data[0]:
		owner = row[10][0][11][0]
		if owner == loginInfo['name']:
			continue
		result.append({
			'id': row[6],
			'sharedKey': row[7],
			'name': row[1],
			'thumb': row[2][0],
			'tsStart': None,
			'tsEnd': None,
			'photosCount': row[3],
			'tsCreated': datetime.datetime.fromtimestamp(row[4]/1000),
			'owner': row[10][0][11][0],
			'ownerFlag': False
		})	
	
	return result

	
def getContent(data):
	photos = []
	videos = []
	for row in data:
		id = row[0]
		url = row[1][0]
		width = row[1][1]
		height = row[1][2]
		ts = datetime.datetime.fromtimestamp(row[2]/1000)
		isVideo = False
		try:
			if '76647426' in row[-1].keys():
				isVideo = True
		except:
			None
		if isVideo:
			format = '=m22'
			if width < 1280:
				format = '=m18'
			videos.append({
				'id': id,
				'url': url + format,
				'thumb': url,
				'ts': ts
			})
		else:
			photos.append({
				'id': id,
				'url': url + '=w' + str(width) + '-h' + str(height) + '-no',
				'thumb': url,
				'ts': ts
			})	
	return({
		'photos': sorted(photos, key=lambda k: k['ts'], reverse=True), 
		'videos': sorted(videos, key=lambda k: k['ts'], reverse=True)
	})	
	
	
def getAlbumContent(pathCookies,albumId,sharedKey=None):
	session = initSession(pathCookies)
	if sharedKey is None:
		url = "https://photos.google.com/album/" + albumId
	else:
		url = 'https://photos.google.com/share/' + albumId + '?key=' + sharedKey
	content = session.get(url).text
	dummy, i = util.substr ("key: 'ds:0', isError:  false , hash:","return",content)
	data = json.loads(util.parseBrackets(content, i, ['[',']']))
	return getContent(data[1])
	

def getRecent(pathCookies):
	session = initSession(pathCookies)
	content = session.get('https://photos.google.com/?pli=1').text
	dummy, i = util.substr ("key: 'ds:2'","return",content)
	data = json.loads(util.parseBrackets(content, i, ['[',']']))
	return getContent(data[0])


def search(pathCookies, searchStr):
	result = {'photos': [], 'videos': [], 'albums': []}
	session = initSession(pathCookies)
	loginInfo = google.getLoginInfo(session)
	content = session.get('https://photos.google.com/search/' + searchStr).text	
	dummy, i = util.substr ("key: 'ds:0', isError:  false , hash:","return",content)
	data = json.loads(util.parseBrackets(content, i, ['[',']']))	
#	util.objToFile(str(data[0]), pathCookies.replace('/cookies','/data.txt'))	
	try:
		result.update(getContent(data[0]))
	except:
		None
	try:
		for row in data[3]:
			result['albums'].append({
				'id': row[0][2][0],
				'name': row[2],
				'thumb': row[1],
				'owner': loginInfo['name'],
				'ownerFlag': True,
				'photosCount': 5,
				'sharedKey': None
		})	
	except:
		None
	return result
	
def getPeople(pathCookies):
	result = []
	session = initSession(pathCookies)
	content = session.get('https://photos.google.com/people').text	
	dummy, i = util.substr ("key: 'ds:1'","return",content)
	data = json.loads(util.parseBrackets(content, i, ['[',']']))	
#	util.objToFile(str(data[0][0][0][0]), pathCookies.replace('/cookies','/data.txt'))
	for row in data[0][0][0][0]:
		if len(row[1]) < 1:
			continue
		id = row[4][0]
		result.append({
			'id': row[8],
			'name': row[1],
			'thumb': row[2]
		})	
	return result

