import requests
from bs4 import BeautifulSoup
import json
import urlparse
import urllib

def getPrograms(liveOnly=False):
	result = []	
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
	}
	url = 'http://tnt-online.ru/programs.htm'
	s = requests.Session()
	soup = BeautifulSoup(s.get(url, headers=headers).text, "html.parser")
	data = soup.find('div',{'id' : 'all-videos'})
	for tag in data.find_all('div',recursive=False):
		result.append({			
			'name': tag.find('b').find('a').get_text(),
			'url': tag.find('b').find('a')['href'],
			'thumb': tag.find('img')['src'],
			'description': ''
		})
	return (result)	


def getEpisodes(urlProgram):
	try:
		episodes = getEpisodes1(urlProgram)
	except:
		episodes = getEpisodes2(urlProgram)
	return episodes
	

def getEpisodes2(urlProgram):
	result = []	
	s = requests.Session()
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',		
		'Referer': urlProgram
	}
	for page in range(1,60):
		params = {'spage': str(page)}
		url = urlProgram + 's01e01'
		soup = BeautifulSoup(s.get(url, headers=headers, params = params).text, "html.parser")
		for tag in soup.find_all('div', class_="thumb-video"):									
			result.append({
				'name': tag.find('div', class_='link').find('a').get_text(),
				'url': urlProgram + tag.find('a')['href'].replace('/',''),
				'thumb': tag.find('img')['src'],
				'description': tag.find('a')['title']
			})
		next = soup.find('input', {'href': '?spage=' + str(page+1)})
		if next is None:
			break
	return(result)
	
	
def getEpisodes1(urlProgram):
	result = []	
	url = 'http://tnt-online.ru/ajax/series'
	params = {
		'name': urlProgram.replace('.tnt-online.ru/','').replace('http://',''),
		'per_page': '200',
		'sort': 'asc'
	}
	s = requests.Session()
	data = json.loads(s.get(url, params=params).text)
	for ep in data['data']:
		result.append({			
			'name': ep['title_format'],
			'url': ep['url'],
			'thumb': ep['icon_big'],
			'description': ''
		})
	return (result)
	
	
	
def getStreams(urlEpisode):
	s = requests.Session()
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',	
	}
	soup = BeautifulSoup(s.get(urlEpisode, headers=headers).text, "html.parser")
	urlRuTube = soup.find('iframe', {'id': 'rutube_player_frame'})['src'].split('?')[0]
	idRuTube = urlRuTube.split('/')[-1]
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',	
		'Referer': urlRuTube
	}	
	url = 'http://rutube.ru/api/play/options/' + idRuTube + '/'	
	params = {
		'format': 'json',
		'sqr4374_compat': 1,
		'no_404': 'true',
		'referer': urlRuTube
	}
	url = url + '?' + urllib.urlencode(params)
	params = {
		'urlText': url
	}
	url = 'http://ru4.gsr.awhoer.net/home287/cmd'	
	data = json.loads(s.get(url, params=params, headers=headers).text)
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
