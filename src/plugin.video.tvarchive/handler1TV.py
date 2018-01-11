import requests
from bs4 import BeautifulSoup
import json
import util
import urllib

_userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'

def getPrograms():
	result = []	
	headers = {
		'User-Agent': _userAgent,
		'Referer': 'https://www.1tv.ru/shows?all'
	}
	url = 'https://www.1tv.ru/shows?all'
	s = requests.Session()
	s.verify = False
	soup = BeautifulSoup(s.get(url, headers=headers).text, "html.parser")
	data = soup.find('div', class_='shows')
	for tag in data.find_all('a',{'target': '_self'}):
		result.append({			
			'name': tag.get_text(),
			'url': 'https://www.1tv.ru' + tag['href'],
			'thumb': ''						
		})
	return (result)	

#https://www.1tv.ru/shows/budushee-za-uglom


def getEpisodes(urlProgram):
	result = []	
	s = requests.Session()
	s.verify = False
	headers = {
		'User-Agent': _userAgent				
	}
	soup = BeautifulSoup(s.get(urlProgram, headers=headers).text, "html.parser")
	csrftoken = soup.find('meta', {'name': 'csrf-token'})['content']
	tag = soup.find('div',{'data-type':'collection'})
	collectionId = tag['data-id']
	
	url = 'https://www.1tv.ru/video_materials.json'
	params = {
		'collection_id': collectionId,
		'single': 'false',
		'sort': 'none'
	}
	data = json.loads(s.get(url, params=params, headers=headers).text)
	for episode in data:
		streams = []
		for i in reversed(range(3)):
			streams.append('http:' + episode['mbr'][i]['src'])
		result.append({			
			'name': episode['title'],
			'streams': streams,
			'thumb': 'http:' + episode['poster_thumb']
		})
	
	
#	collectionPosition = tag['data-position']
#	headers = {
#		'User-Agent': _userAgent,
#		'Referer': urlProgram,
#		'X-CSRF-Token': csrftoken
#	}
#	url = 'https://www.1tv.ru/collections/' + collectionId + '/items'
#	params = {
#		'limit': '50',
#		'offset': '0',
#		'position': collectionPosition,
#		'view_type': 'tile'
#	}
#	data = s.get(url, params=params, headers=headers).text
#	html, i = util.substr ("var collection_items_html = '","';",data)	
#	html = html.replace('\\"','"')
#	soup = BeautifulSoup(html, "html.parser")
#	for tag in soup.find_all('div',{'data-role': 'collection_item_card'}):
#		result.append({			
#			'name': tag.find('a')['data-title'],
#			'url': 'https://www.1tv.ru' + tag.find('a')['data-modal-url'].split('.js')[0],
#			'thumb': 'http:' + tag.find('img', class_='w_collection_item_img')['src']
#		})
	return(result)
	
	
