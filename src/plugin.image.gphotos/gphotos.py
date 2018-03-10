from bs4 import BeautifulSoup
import requests
import util
import json
	

def getAlbums(session):
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
	
	
def getAlbumPhotos(albumId, session):
	result = []
	content = session.get("https://photos.google.com/album/" + albumId).text
	dummy, i = util.substr ("key: 'ds:0', isError:  false , hash:","return",content)
	data = json.loads(util.parseBrackets(content, i, ['[',']']))
	i = 1
	for row in data[1]:
		result.append({
			'id': row[0],
			'name': 'Photo ' + str(i),
			'thumb': row[1][0],
			'width': row[1][1],
			'height': row[1][2],
			'fullsize': row[1][0] + '=w' + str(row[1][1]) + '-h' + str(row[1][2]) + '-no'	
		})	
		i = i + 1
	return(result)



