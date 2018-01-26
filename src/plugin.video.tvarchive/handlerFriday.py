import requests
from bs4 import BeautifulSoup
import json
import urlparse
import urllib


def getPrograms(liveOnly=False):
	result = []	
	s = requests.Session()
	s.verify = False
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
	}
	for page in range (1,8):
		found = False
		url = 'https://show.friday.ru/' + str(page)
		soup = BeautifulSoup(s.get(url, headers=headers).text, "html.parser")	
		for tag in soup.find_all('div', class_='list-item'):
			found = True
			result.append({			
				'name': tag.find('h3').get_text(),
				'url': tag.find('a')['href'],
				'thumb': 'https://show.friday.ru' + tag.find('img')['src'],
				'description': tag.find('p').get_text()
			})
		if not found:
			break
	return (result)	


def getEpisodes(urlProgram, forceLowQuality=False):
	result = []	
	s = requests.Session()
	s.verify = False
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',		
	}
	for page in range(1,20):
		found = False
		url = urlProgram + 'videos/' + str(page)
		soup = BeautifulSoup(s.get(url, headers=headers).text, "html.parser")
		for tag in soup.find_all('div', {'itemtype':'http://schema.org/VideoObject'}):									
			found = True
			result.append({
				'name': tag.find('h3').get_text(),
				'url': tag.find('a', class_='clip')['href'],
				'thumb': tag.find('img')['src'],
				'description': tag.find('meta', {'itemprop':'description'})['content'] + ' (' + tag.find('meta', {'itemprop':'uploadDate'})['content'].split('T')[0] +')',
				'duration': int(tag.find('meta', {'itemprop':'duration'})['content'])
			})
		if not found:
			break
	return(result)
	
	
#def getStream(urlEpisode, forceLowQuality=False):
#	s = requests.Session()
#	s.verify = False
#	headers = {
#		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',	
#	}
#	soup = BeautifulSoup(s.get(urlEpisode, headers=headers).text, "html.parser")
#	urlRuTube = soup.find('iframe', {'id': 'rutube_player_frame'})['src'].split('?')[0]
#	idRuTube = urlRuTube.split('/')[-1]
#	headers = {
#		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',	
#		'Referer': urlRuTube
#	}	
#	url = 'http://rutube.ru/api/play/options/' + idRuTube + '/'	
#	params = {
#		'format': 'json',
#		'sqr4374_compat': 1,
#		'no_404': 'true',
#		'referer': urlRuTube
#	}
#	data = json.loads(s.get(url, params=params, headers=headers).text)
#	data = s.get(data['video_balancer']['m3u8']).text.replace('http',"\n"+'http')
#	for line in data.splitlines():
#		if line.startswith('http'):
#			return line
#	return ''

def getStreams(urlEpisode):
	s = requests.Session()
	s.verify = False
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

