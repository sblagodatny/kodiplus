# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import util
import json
import re
import urllib
import time
import sys
import HTMLParser
	

def getXCSRF(session):
	loginInfo = getUserDetails(session)
	if loginInfo is not None:
		return loginInfo['xcsrf']
	data = BeautifulSoup(session.get('https://plus.kinopoisk.ru/').content, "html.parser")
	data = data.find(class_="i-bem")['data-bem']
	if 'csrf' not in data:
		raise Exception('Robot protection')
	xcsrf = json.loads(data)['page']['csrf']	
	return xcsrf

	
def login(pathCookies, user, password):						
	session=initSession()	
	xcsrf = getXCSRF(session)		
	session.headers['X-CSRF-Token']=xcsrf
	session.headers['Content-Type']='application/x-www-form-urlencoded; charset=UTF-8'
	session.headers['X-Requested-With']='XMLHttpRequest'
	data={'login': user, 'password': password}
	reply = json.loads(session.post("https://plus.kinopoisk.ru/user/resolve-by-password", data=data).content)
	if reply['status'] != 'ok':
		raise Exception('Invalid credentials')					
	loginInfo = user + '&' + str(reply['userParams']['uid']) + '&' + str(time.time()) + '&' + xcsrf
	util.setCookie(session, 'www.kinopoisk.com', 'MyLoginInfo', loginInfo)
	util.saveCookies(session, pathCookies)
	

def getUserDetails(session):	
	try:
		loginInfo = session.cookies._find(name='MyLoginInfo', domain='www.kinopoisk.com').split('&')
		return ({
			'user': loginInfo[0],
			'uid': loginInfo[1],
			'ts': float(loginInfo[2]),
			'xcsrf': loginInfo[3]
		})
	except:
		return None	

		
def initSession(pathCookies=None):
	session = requests.Session()
	session.verify = False
	if pathCookies is not None:
		util.loadCookies(session, pathCookies)
	util.setUserAgent(session, 'chrome')
	session.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
	session.headers['Accept-Encoding'] = 'gzip, deflate, br'
	session.headers['Accept-Language'] = 'en-US,en;q=0.9,he-IL;q=0.8,he;q=0.7,ru-RU;q=0.6,ru;q=0.5'
	session.headers['Upgrade-Insecure-Requests'] = '1'
	session.headers['Referer'] = 'https://plus.kinopoisk.ru/'
	return session


	
		
def parseContent(content):
	result = []
	if 'captcha' in content:
		return result
	data, dummy = util.substr("window._state = '","'",content)
	data = urllib.unquote(data).replace('%','\\').decode('unicode-escape').encode('utf8')
	data = json.loads(data)
	for d in data['movies'].values():	
		if 'rating' not in d['ratingData'].keys():
			continue
		try:
			rating = float(d['ratingData']['rating']['rate'])
			if rating < 1:
				continue
		except:
			continue
		row = {
			'id': d['id'],
			'type': d['type'], # SHOW/MOVIE
			'title': util.unescape(d['title']),
			'originalTitle': None,
			'year': util.unescape(d['year']),
			'favorite': d['favorite'], # Boolean
			'rate': d['ratingData']['rating']['rate'],
			'watched': None,
			'genres': [f['name'] for f in d['genres']],
			'countries': d['countries']
		}
		originalTitle = util.unescape(d['originalTitle'])
		if len(originalTitle) > 0 and originalTitle != row['title']:
			row['originalTitle'] = originalTitle	
		row['myrate'] = '12345'
		if 'myRate' in d['ratingData'].keys():
			row['watched'] = d['ratingData']['myRate']['date'][0:10]					
		result.append(row)			
	return result

def pageLoop(session, url, params, pages):
	result = []
	p = params
	for page in range(1,pages+1):
		p['page']=page
		content = parseContent(session.get(url=url, params=p).content)
		result = result + content
		if len(content)<9:
			break
	return result
	
def getFavorites(pathCookies):
	session = initSession(pathCookies)
	url = 'https://plus.kinopoisk.ru/user/' + getUserDetails(session)['uid'] + '/favorites/'	
	return pageLoop(session, url, {}, 4)	

	
def setFavorites(pathCookies, id, favorites):
	session = initSession(pathCookies)
	xcsrf = getXCSRF(session)
	session.headers['X-CSRF-Token']=xcsrf
	session.headers['Content-Type']='application/x-www-form-urlencoded; charset=UTF-8'
	session.headers['X-Requested-With']='XMLHttpRequest'
	if favorites:
		url = 'https://plus.kinopoisk.ru/favorites/add/'
	else:
		url = 'https://plus.kinopoisk.ru/favorites/delete/'
	params = {'movieId': id}
	reply = session.post(url=url,data=params).status_code
	if reply != 200:
		raise Exception('Unable to set favorites')
	

def setWatched(pathCookies, id, watched):
	session = initSession(pathCookies)
	xcsrf = getXCSRF(session)
	session.headers['X-CSRF-Token']=xcsrf
	session.headers['Content-Type']='application/x-www-form-urlencoded; charset=UTF-8'
	session.headers['X-Requested-With']='XMLHttpRequest'		
	if watched:
		url = 'https://plus.kinopoisk.ru/film/' + id + '/rates/update/'
	else:
		url = 'https://plus.kinopoisk.ru/film/' + id + '/rates/delete/'
	reply = session.post(url=url).status_code
	if reply not in [200,201]:
		raise Exception('Unable to set watched')
	
		
def searchByTitle(pathCookies, title, type=None):
	session = initSession(pathCookies)
	url = 'https://plus.kinopoisk.ru/search/'
	if type == 'MOVIE':
		url = url + 'films/'
	if type == 'SHOW':
		url = url + 'series/'
	params = {'text': title}
	content = pageLoop(session, url, params, 4)
	result = []
	titlestrict = title.split(' ')[0].lower()
	for item in content:
		if titlestrict in item['title'].lower() or titlestrict in util.nvl(item['originalTitle'],'').lower():		
			result.append(item)
	return result


def getSeasons(pathCookies,id):
	session = initSession(pathCookies)
	session.headers['X-Requested-With']='XMLHttpRequest'
	session.headers['Referrer']='https://plus.kinopoisk.ru/film/' + id + '/details/series'
	seasons = {}
	for i in range (1,15):	
		reply = session.get('https://plus.kinopoisk.ru/film/' + id + '/details/series/s' + str(i) + '/')
		if  reply.status_code != 200:
			break
		if 'captcha' in reply.content:
			return None
		data=json.loads(reply.content)
		data = data['content']
		if 'button_state_release' in data:
			watched = False
		else:
			watched = True
		seasons.update({i: watched})
	return seasons
	
	
def setSeasonWatched(pathCookies, id, season, state):	
	session = initSession(pathCookies)
	xcsrf = getXCSRF(session)
	session.headers['X-CSRF-Token']=xcsrf
	session.headers['X-Requested-With']='XMLHttpRequest'
	session.headers['Content-Type']='application/x-www-form-urlencoded; charset=UTF-8'
	session.headers['Referrer']='https://plus.kinopoisk.ru/film/' + id + '/details/series/s' + str(season) + '/'
	url = 'https://plus.kinopoisk.ru/serials/' + id + '/views/'
	if state:
		url = url + 'seen/all/'
	else:
		url = url + 'unseen/all/'	
	data = {'seasonNum': str(season)}
	reply = session.post(url, data = data).status_code
	if reply not in [200,201]:
		raise Exception('Unable to set season watched')
		

def getDetails(pathCookies, id):
	session = initSession(pathCookies)
	url = 'https://plus.kinopoisk.ru/film/' + id + '/'
	soap = BeautifulSoup(session.get(url=url).content, "html.parser")	
	actors=[]
	for tag in soap.find(class_='movie-actors').find_all(class_='person'):
		actors.append({
			'name': tag.find(class_='person__info-name')['content'],
			'role': 'Актер',
			'thumbnail': 'https:' + tag.find(class_='person__photo-image')['srcset'].split(' ')[0]
		})
	directors=[]
	for tag in soap.find(class_='movie-directors').find_all(class_='person'):
		directors.append({
			'name': tag.find(class_='person__info-name')['content'],
			'role': 'Режиссер',
			'thumbnail': 'https:' + tag.find(class_='person__photo-image')['srcset'].split(' ')[0]
		})
	return {
		'description': soap.find(class_="film-description").find('div').get_text(),
		'actors': actors,
		'directors': directors
	}
	
		
def getThumb(id):
	return 'https://www.kinopoisk.ru/images/sm_film/' + id + '.jpg'
	
def getPoster(id):
	return 'https://www.kinopoisk.ru/images/film_big/' + id + '.jpg'
