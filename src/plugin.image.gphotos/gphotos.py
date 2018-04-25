from bs4 import BeautifulSoup
import requests
import util
import json
	
def initSession(pathCookies):
	session = requests.Session()
	session.verify = False
	util.loadCookies(session, pathCookies)
	util.setUserAgent(session, 'chrome')
	return session
	
	
def getAlbums(pathCookies):
	session = initSession(pathCookies)
	result = []
	content = session.get("https://photos.google.com/albums").text
	dummy, i = util.substr ("key: 'ds:2', isError:  false , hash:","return",content)
	data = json.loads(util.parseBrackets(content, i, ['[',']']))
	for row in data[0]:
		result.append({
			'id': row[0],
			'name': row[12]['72930366'][1],
			'thumb': row[1][0]
		})	
	resultsorted = sorted(result, key=lambda k: k['name'], reverse=True) 	
	return(resultsorted)
	
	
def getAlbumContent(pathCookies,albumId):
	session = initSession(pathCookies)
	photos = []
	videos = []
	content = session.get("https://photos.google.com/album/" + albumId).text
	dummy, i = util.substr ("key: 'ds:0', isError:  false , hash:","return",content)
	data = json.loads(util.parseBrackets(content, i, ['[',']']))
#	util.objToFile(str(data),pathCookies.replace('/cookies','/obj.txt'))
	for row in data[1]:
		id = row[0]
		url = row[1][0]
		width = row[1][1]
		height = row[1][2]
		name = 'Photo'
		isVideo = False
		if '76647426' in row[-1].keys():
			name = 'Video'
			isVideo = True
		if isVideo:
			format = '=m22'
			if width < 1280:
				format = '=m18'
			videos.append({
				'id': id,
				'url': url + format,
				'thumb': url,
				'name': name
			})
		else:
			photos.append({
				'id': id,
				'url': url + '=w' + str(width) + '-h' + str(height) + '-no',
				'thumb': url,
				'name': name
			})
	return({'photos': photos, 'videos': videos})

