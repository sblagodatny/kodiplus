# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import util
import json
import re
import urllib
import time
import sys



def getXCSRF(session):
	data = BeautifulSoup(session.get('https://plus.kinopoisk.ru/').content, "html.parser")
	data = data.find(class_="i-bem")['data-bem']
	if 'csrf' not in data:
		raise Exception('Robot protection')
	csrf = json.loads(data)['page']['csrf']	
	return csrf
	

def login(session, user, password):					
	data={'login': user, 'password': password}
	headers = session.headers
	xcsrf = getXCSRF(session)
	session.headers.update({
		'X-CSRF-Token': xcsrf,
		'Referer': 'https://plus.kinopoisk.ru/',
		'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
		'Origin': 'https://plus.kinopoisk.ru',
		'X-Requested-With': 'XMLHttpRequest'
	})	
	session.headers = headers
	reply = json.loads(session.post("https://plus.kinopoisk.ru/user/resolve-by-password", data=data, headers=headers).content)
	if reply['status'] != 'ok':
		raise Exception('Invalid credentials')					
	args = {
			'domain': 'www.kinopoisk.com',
			'expires': None,
			'path': '/',
			'version':0
		}
	loginInfo = {
		'user': user,
		'xcsrf': xcsrf
	}
	session.cookies.set(name='MyLoginInfo',value=util.urlencode(loginInfo), **args)
	session.saveCookies()
		

def loginDetails(session):	
	try:
		loginInfo = session.cookies._find(name='MyLoginInfo', domain='www.kinopoisk.com')
		return (util.urldecode(loginInfo))
	except:
		return None
	
	
def loginVerify (session, user, password):
	loginInfo = loginDetails(session)
	if loginInfo is not None:
		if loginInfo['user'] == user:
			return
	login(session,user,password)		

	
def getDetails(session, id):
	headers = session.headers
	session.headers.update({'Referrer': 'https://plus.kinopoisk.ru/search/'})	
	data = BeautifulSoup(session.get('https://plus.kinopoisk.ru/film/' + id + '/').content, "html.parser")
	try:
		description = data.find("div", {"itemprop" : "description"}, class_='kinoisland__content').get_text()
	except:
		description = ''
	try:
		rating = data.find(class_='rating-button__rating').get_text()
	except:
		rating = ''
	try:
		tags = data.find(class_='movie-tags')['content']
	except:
		tags = ''
	try:
		data = data.find(class_='film-header__production').get_text().replace('&thinsp;&ndash;&thinsp;',' - ')
		year = data.split(',')[-1][1:]
		country = data.replace(year,'')[:-1]
	except:
		country = ''
		year = ''		
	result = {
		'description': description,
		'rating' : rating,
		'country': country,
		'year': year,
		'genre': tags,
		'director': 'Unknown'
	}
	session.headers = headers
	return result
		

def getSeasons(session,id):
	seasons = []
	headers = session.headers
	session.headers.update({'Referrer': 'https://plus.kinopoisk.ru/film/' + id + '/details/series','X-Requested-With': 'XMLHttpRequest'})	
	iw = 0
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
		if watched:
			iw = i
	session.headers = headers
	return {'seasonsTotal': i-1, 'seasonsWatched': iw}
	
	
def setSeasonWatched(session,id,season, state):	
	loginInfo = loginDetails(session)
	if loginInfo is None:
		raise Exception ("Not logged in")
	headers = session.headers
	session.headers.update({
		'Referrer': 'https://plus.kinopoisk.ru/film/' + id + '/details/series/s' + season + '/',
		'Origin': 'https://plus.kinopoisk.ru',
		'X-Requested-With': 'XMLHttpRequest',
		'X-CSRF-Token': loginInfo['xcsrf']
	})	
	url = 'https://plus.kinopoisk.ru/serials/' + id + '/views/'
	if state:
		url = url + 'seen/all/'
	else:
		url = url + 'unseen/all/'
	
	data = {'seasonNum': season}
	reply = session.post(url, data = data)
	session.headers = headers
	
	
