from bs4 import BeautifulSoup
import requests
import util
import json
import datetime
	
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
			'sharedKey': row[12]['72930366'][5],
			'name': row[12]['72930366'][1],
			'thumb': row[1][0],
			'tsStart': datetime.datetime.fromtimestamp(row[12]['72930366'][2][0]/1000),
			'tsEnd': datetime.datetime.fromtimestamp(row[12]['72930366'][2][1]/1000)
		})	
	resultsorted = sorted(result, key=lambda k: k['name'], reverse=True) 	
	return(resultsorted)
	

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
	return({'photos': photos, 'videos': videos})	
	
	
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


def search(pathCookies, searchStr):
	result = {'photos': [], 'videos': [], 'albums': []}
	session = initSession(pathCookies)
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
				'thumb': row[1]
		})	
	except:
		None
	return result