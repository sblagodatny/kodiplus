import requests
from bs4 import BeautifulSoup
import json
import urlparse
import urllib


def contentVideos(contentId, seasonId):
	result = []
	s = requests.Session()
	s.verify = False
	url = 'https://rutube.ru/api/metainfo/tv/' + contentId + '/video'
	for page in range(1,10):
		params = {
			'sort': 'series_a',
			'season': seasonId,
			'type': '2',
			'page': page
		}
		data = json.loads(s.get(url=url, params=params).text)
		for video in data['results']:
			result.append({
				'id': video['id'],
				'name': video['title'],
				'thumb': video['thumbnail_url'],
				'description': video['description'],
				'duration': video['duration'],
				'episode': video['episode'],
				'created': video['created_ts'].split('T')[0]
			})
		if not data['has_next']:
			break
						
	return result
	

def searchContent(searchstr):
	s = requests.Session()
	s.verify = False
	url = 'https://rutube.ru/api/search/promo/tv/'
	params = {
		'query': searchstr
	}	
	data = json.loads(s.get(url=url, params=params).text)
	try:
		result = {
			'id': data['id'],
			'type': data['type']['title'],
			'name': data['name'],		
			'thumb': 'https:' + data['picture'],
			'description': data['description'],
			'seasons': data['seasons_count'],
			'videos': data['video_count']
		}
		return result
	except:
		return None
	


def doProxy(url, s):
	params = {'urlText': url}
	proxy = 'http://ru4.gsr.awhoer.net/home287/cmd'	
	return s.get(proxy, params=params).text
	
	
def getStream(videoId):
	s = requests.Session()
	s.verify = False	
	url = 'http://rutube.ru/api/play/options/' + videoId + '/'	
	params = {
		'format': 'json',
		'sqr4374_compat': 1,
		'no_404': 'true'
	}
	data = json.loads(doProxy(url + '?' + urllib.urlencode(params),s))
	url = data['video_balancer']['m3u8']
	url = 'http://bl.rutube.ru/route/' + url.split('/route/')[1]
	data = s.get(url).text.splitlines()
	streams = {}
	for line in data:
		if line.startswith('http'):
			quality = line.split('?i=')[1].split('_')[0]
			streams.update({quality: line})
	if '640x360' in streams.keys():
		return streams['640x360']
	else:
		return streams [streams.keys()[0]]

