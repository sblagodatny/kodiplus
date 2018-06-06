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
import xbmcgui
	


def login(pathCookies, user, password):						
	session=initSession()	
	## Step 1 ##
	data = {'retPath': 'https://www.kinopoisk.ru'}
	content = BeautifulSoup(session.get('https://plus.kinopoisk.ru/embed/login/', data=data).content, "html.parser")
	data = json.loads(content.find(class_="i-bem")['data-bem'])
	xcsrf = data['page']['csrf']
	## Step 2 ##
	session.headers['X-CSRF-Token']=xcsrf
	session.headers['Content-Type']='application/x-www-form-urlencoded; charset=UTF-8'
	session.headers['X-Requested-With']='XMLHttpRequest'
	data={'login': user, 'password': password}
	reply = json.loads(session.post("https://plus.kinopoisk.ru/user/resolve-by-password", data=data).content)
	if reply['status'] != 'ok':
		raise Exception('Invalid credentials')					
	## Save ##
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
			'xcsrftoken': loginInfo[3]
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
	session.headers['Referer'] = 'https://www.kinopoisk.ru/'
	return session



def getFolders(pathCookies):
	session = initSession(pathCookies)	
	data = BeautifulSoup(session.get('https://www.kinopoisk.ru/mykp/movies/').content, "html.parser").find('ul',{'id': 'folderList'})
	result = {}
	for tag in data.find_all('li'):
		id = tag['data-id']
		name = tag.find('a')
		if name is None:
			name = tag.find('span')
		name = name.get_text()
		if ' (' in name:
			name = name.split(' (')[0]
		result.update({name.encode('utf8'): id})		
	return result

	
def getFolderContent(pathCookies, folder):
	session = initSession(pathCookies)	
	content = session.get('https://www.kinopoisk.ru/mykp/movies/list/type/' + folder + '/').content
	data = BeautifulSoup(content, "html.parser").find('ul',{'id': 'itemList'})
	result = []
	for tag in data.find_all('li'):	
		info = tag.find(class_='info').findAll('span')
		usercode, i = util.substr("user_code: '", "'",str(tag))
		item = {
			'id': tag['data-id'],
			'type': 'MOVIE', # SHOW/MOVIE
			'title': cleanseTitle(tag.find(class_='name').get_text()),
			'originalTitle': info[0].get_text().split('(')[0].strip(),
			'year': info[0].get_text().split('(')[-1].split(')')[0],			
			'rate': tag.find(class_='kpRating').find('span').get_text().split(' ')[0],
			'watched': False,
			'genres': info[2].get_text().replace('(','').replace(')',''),
			'countries': info[1].get_text().split('реж.')[0].replace(',','').replace("\n",'').replace(' ',''),
			'usercode': usercode
		}	
		if ' (сериал)' in item['title']:
			item['title'] = item['title'].replace(' (сериал)','')
			item['type'] = 'SHOW'
		myrating = tag.find(class_='vote_widget').find_next().get_text().split("rating: '")[1].split("'")[0]	
		if myrating != '':
			item['watched'] = True
		if len(item['originalTitle'])==0:
			item['originalTitle'] = None
		result.append(item)	
	return result	


def searchByTitle(pathCookies, title, type):
	session = initSession(pathCookies)
	url = 'https://www.kinopoisk.ru/index.php'
	params = {
		'level': '7',
		'from': 'forma',
		'result': 'adv',
		'm_act[from]': 'forma',
		'm_act[what]': 'content',
		'm_act[find]': title,
		'm_act[content_find]': 'film'	
	}
	if type == 'SHOW':
		params['m_act[content_find]'] = 'serial'	
	data = BeautifulSoup(session.get(url, params=params).content, "html.parser")
	result = []	
	for tag in data.find_all(class_="element"):		
		item = {
			'id': tag.find(class_="info").find('a')['data-id'],
			'type': 'MOVIE', # SHOW/MOVIE
			'title': cleanseTitle(tag.find(class_="name").find('a').get_text()),
			'originalTitle': None,
			'year': '',			
			'rate': '',
			'watched': False,
			'genres': '',
			'countries': '',
			'usercode': 'None'
		}	
		if ' (сериал)' in item['title']:
			item['title'] = item['title'].replace(' (сериал)','')
			item['type'] = 'SHOW'
		try:
			item['year'] = tag.find(class_="year").get_text()
		except:
			continue
		try:
			item['rate'] = tag.find(class_='rating').get_text()
		except:
			continue
		try:
			myrating = tag.find(class_='my_vote').get_text()
			item['watched'] = True
		except:
			None
		try:
			originalTitle = tag.findAll(class_='gray')[0].get_text()
			if ',' in originalTitle:
				item['originalTitle'] = originalTitle.split(',')[0].strip()
		except:
			None
		try:
			info = tag.findAll(class_='gray')[1].get_text()
			item['countries'] = info.split('реж')[0].replace(',','').strip()
			item['genres'] = info.split('(')[1].split(')')[0]
		except:
			None
		result.append(item)									
	return result	
	
	
def cleanseTitle(name):
	result = name
	result = result.replace(' (видео)','')
	result = result.replace(' (ТВ)','')
	result = result.replace(' (мини-сериал)',' (сериал)')
	return result

		
def getDetails(pathCookies, id):
	session = initSession(pathCookies)
	url = 'https://www.kinopoisk.ru/film/' + id
	content = session.get(url=url).content
	soap = BeautifulSoup(content, "html.parser")	
	usercode, i = util.substr("user_code:'", "'",content)
	result = {
		'description': soap.find(class_='film-synopsys').get_text(),
		'usercode': usercode
	}
	try:
		result['seasons'] = int(soap.find('title').get_text().split(' сезон')[0].split(' ')[-1])
	except:
		None
	return result
	
	
def getCast(pathCookies, id, role):
	session = initSession(pathCookies)
	data = BeautifulSoup(session.get('https://www.kinopoisk.ru/film/' + id + '/cast/who_is/' + role + '/').content, "html.parser")
	result = []
	for tag in data.find_all(class_='actorInfo'):
		person = tag.find(class_='name').find('a').get_text()
		photo = None
		try:
			photo = 'https://www.kinopoisk.ru/' + tag.find(class_='photo').find('img')['title']
		except:
			None
		result.append({'name': person, 'thumbnail': photo, 'role': role}) 
	return result
		
	
	
	
	
def getThumb(id):
	return 'https://www.kinopoisk.ru/images/sm_film/' + id + '.jpg'
	
def getPoster(id):
	return 'https://www.kinopoisk.ru/images/film_big/' + id + '.jpg'
	
	
def setWatched(pathCookies,id,state,usercode='None'):		
	session = initSession(pathCookies)
	session.headers['X-Requested-With']='XMLHttpRequest'
	data = {
		'token': getUserDetails(session)['xcsrftoken'],
		'id_film': id
	}
	util.setCookie(session, '.kinopoisk.ru', '_csrf/csrf_token', data['token'])	
	if state:
#		data['act'] = 'add'
#		session.get("https://www.kinopoisk.ru/handler_vote.php" + '?' + urllib.urlencode(data))
#		del data['act']
		data['vote'] = '7'
		data['c'] = usercode
		if usercode == 'None':
			data['c'] = getDetails(pathCookies, id)['usercode']
		session.get("https://www.kinopoisk.ru/handler_vote.php" + '?' + urllib.urlencode(data))
	else:
		data['act'] = 'kill_vote'
		session.get("https://www.kinopoisk.ru/handler_vote.php" + '?' + urllib.urlencode(data))
		data['act'] = 'delete'
		session.get("https://www.kinopoisk.ru/handler_vote.php" + '?' + urllib.urlencode(data))


def setFolder(pathCookies,id,folder,state):	
	session = initSession(pathCookies)
	session.headers['X-Requested-With']='XMLHttpRequest'
	data = {
		'token': getUserDetails(session)['xcsrftoken'],
		'id_film': id
	}
	util.setCookie(session, '.kinopoisk.ru', '_csrf/csrf_token', data['token'])	
	if state:
		data['mode'] = 'add_film'
		data['to_folder'] = folder
	else:
		data['mode'] = 'del_film'
		data['from_folder'] = folder
	session.get("https://www.kinopoisk.ru/handler_mustsee_ajax.php" + '?' + urllib.urlencode(data))
