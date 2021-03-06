# coding: utf-8

import requests
from bs4 import BeautifulSoup
import json
import urlparse
import urllib


_userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'


def getCategories():
	return [
		{'name': 'Теле-Проекты (текущий сезон)', 'url': 'https://www.1tv.ru/shows'}
#		{'name': 'Сериалы', 'url': 'https://kino.1tv.ru/series'}
	]
	

def getPrograms(urlCategory):
	result = []	
	headers = {
		'User-Agent': _userAgent,
	}
	s = requests.Session()
	s.verify = False
	soup = BeautifulSoup(s.get(urlCategory, headers=headers).text, "html.parser")
	data = soup.find('section', class_='projects')	
	for tag in data.find_all('a',{'target': '_self'}):
		result.append({			
			'name': tag.find('img')['alt'],
			'url': 'https://www.1tv.ru' + tag['href'],
			'thumb': 'http:' + tag.find('img')['src'],					
			'description': tag.find('p').get_text()
		})
	return result
	

def getEpisodes(urlProgram):
	result = []	
	s = requests.Session()
	s.verify = False
	headers = {
		'User-Agent': _userAgent				
	}
	soup = BeautifulSoup(s.get(urlProgram, headers=headers).text, "html.parser")
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
		name = episode['title']
		description = ''
		if '.' in name:
			description = name
			name = description.split('.')[0]
		stream = 'http:' + episode['mbr'][0]['src']
		result.append({			
			'name': name,
			'url': stream,
			'thumb': 'http:' + episode['poster_thumb'],
			'description': description,
			'duration': int(episode['duration'])
		})
	return(result)


def getStream(urlVideo):
	return urlVideo
