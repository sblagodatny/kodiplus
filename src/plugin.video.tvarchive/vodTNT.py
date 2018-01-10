import requests
from bs4 import BeautifulSoup
import json

def getPrograms():
	result = []	
	url = 'http://tnt-online.ru/programs.htm'
	s = requests.Session()
	soup = BeautifulSoup(s.get(url).text, "html.parser")
	data = soup.find('div',{'id' : 'all-videos'})
	for tag in data.find_all('div',recursive=False):
		result.append({			
			'name': tag.find('b').find('a').get_text(),
			'url': tag.find('b').find('a')['href'],
			'thumb': tag.find('img')['src']						
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
				'name': tag.find('a')['title'],
				'url': urlProgram + tag.find('a')['href'].replace('/',''),
				'thumb': tag.find('img')['src']
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
			'name': ep['name'],
			'url': ep['url'],
			'thumb': ep['icon_big'],
			'season': ep['season'],
			'episode': ep['episode']
		})
	return (result)
	
	
def getStream(urlEpisode):
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
	data = json.loads(s.get(url, params=params, headers=headers).text)
	return data['video_balancer']['m3u8']
	