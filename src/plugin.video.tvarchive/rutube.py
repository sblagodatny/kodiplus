# coding: utf-8


import requests
from bs4 import BeautifulSoup
import json
import urlparse
import urllib


def getCategories(channel):
	result = []	
	s = requests.Session()
	s.verify = False
	url = 'https://rutube.ru/feeds/' + channel
	soup = BeautifulSoup(s.get(url).text, "html.parser")	
	for tag in soup.find_all('a', class_='tab-link'):
		if tag['title'] not in ['Новое видео','Резиденты','Скоро']:
			result.append({			
				'name': tag['title'],
				'url': tag['href']
			})
	return (result)	



def getPrograms(urlCategory):
	result = []	
	s = requests.Session()
	s.verify = False
	soup = BeautifulSoup(s.get(urlCategory).text, "html.parser")	
	for tag in soup.find_all('article', class_='b-cards__item'):
		result.append({			
			'name': tag.find('div',class_='title').find('span').get_text(),
			'url': tag.find('a',class_='b-cards__tag_item-link')['href'],
			'thumb':  tag.find('div',class_='bg-img')['style'].replace('background-image:url(','').replace(');',''),
			'description': tag.find('div',class_='descr').get_text()
		})
	return (result)	


def getEpisodes(urlProgram):
	result = []
	s = requests.Session()
	s.verify = False
	url = urlProgram.replace('rutube.ru/','rutube.ru/api/') + '/video'
	for season in range(1,20):
		for page in range(1,10):
			params = {
				'sort': 'series_a',
				'season': str(season),
				'type': '2',
				'page': page
			}
			data = json.loads(s.get(url=url, params=params).text)
			for video in data['results']:
				result.append({
					'url': video['id'],
					'name': video['title'],
					'thumb': video['thumbnail_url'],
					'description': video['description'],
					'duration': video['duration'],
				})
			if not data['has_next']:
				break						
#		if not data['has_next']:
#				break
	return result	


def doProxy(url, s):
	params = {'urlText': url}
	proxy = 'http://ru4.gsr.awhoer.net/home287/cmd'	
	return s.get(proxy, params=params).text
	
	
def getStream(urlVideo):
	s = requests.Session()
	s.verify = False	
	url = 'http://rutube.ru/api/play/options/' + urlVideo + '/'	
	params = {
		'format': 'json',
		'sqr4374_compat': 1,
		'no_404': 'true'
	}
	data = json.loads(s.get(url, params=params).text)
	if 'video_balancer' not in data:
		data = json.loads(doProxy(url + '?' + urllib.urlencode(params),s))
	url = data['video_balancer']['m3u8']
	url = 'http://bl.rutube.ru/route/' + url.split('/route/')[1]
	data = s.get(url).text.splitlines()
	streams = {}
	for line in data:
		if line.startswith('http'):
			quality = line.split('?i=')[1].split('_')[0]
			streams.update({quality: line})
	quality = '640x360'
	if quality in streams.keys():
		return(streams[quality])
	else:
		return(streams [streams.keys()[0]])		
	