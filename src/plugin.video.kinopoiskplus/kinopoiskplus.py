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
		result.update({id: name})		
	return result

	
def getFolderContent(pathCookies, folder):
	session = initSession(pathCookies)	
	data = BeautifulSoup(session.get('https://www.kinopoisk.ru/mykp/movies/list/type/' + folder + '/').content, "html.parser").find('ul',{'id': 'itemList'})
	result = []
	for tag in data.find_all('li'):	
		info = tag.find(class_='info').findAll('span')
		item = {
			'id': tag['data-id'],
			'type': 'MOVIE', # SHOW/MOVIE
			'title': cleanseTitle(tag.find(class_='name').get_text()),
			'originalTitle': info[0].get_text().split('(')[0].strip(),
			'year': info[0].get_text().split('(')[-1].split(')')[0],			
			'rate': tag.find(class_='kpRating').find('span').get_text().split(' ')[0],
			'watched': False,
			'genres': info[2].get_text().replace('(','').replace(')',''),
			'countries': info[1].get_text().split('реж.')[0].replace(',','').replace("\n",'').replace(' ','')
		}	
		if ' (сериал)' in item['title']:
			item['title'] = item['title'].replace(' (сериал)','')
			item['type'] = 'SHOW'
		myrating = tag.find(class_='vote_widget').find_next().get_text().split("rating: '")[1].split("'")[0]	
		if myrating != '':
			item['watched'] = True
		result.append(item)	
		if len(item['originalTitle'])==0:
			item['originalTitle'] = None
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
	soap = BeautifulSoup(session.get(url=url).content, "html.parser")	
	result = {
		'description': soap.find(class_='film-synopsys').get_text()
	}
	return result
	
	
def getCast(pathCookies, id, role):
	session = initSession(pathCookies)
	data = BeautifulSoup(session.get('https://www.kinopoisk.ru/film/' + id + '/cast/who_is/' + role + '/').content, "html.parser")
	result = []
	for tag in data.find_all(class_='actorInfo'):
		person = tag.find(class_='name').find('a').get_text()
		photo = 'https://www.kinopoisk.ru/' + tag.find(class_='photo').find('img')['title']
		result.append({'name': person, 'role': role, 'thumbnail': photo}) 
	return result
		
	
	
	
	
def getThumb(id):
	return 'https://www.kinopoisk.ru/images/sm_film/' + id + '.jpg'
	
def getPoster(id):
	return 'https://www.kinopoisk.ru/images/film_big/' + id + '.jpg'
