# coding: utf-8

import util
import urllib
from bs4 import BeautifulSoup
import requests
import time


	
def login(pathCookies, user, password):
	session = requests.Session()
	session.verify = False
	util.setUserAgent(session, 'chrome')
	session.headers.update ({
		'Accept-Encoding': 'gzip, deflate',
		'Content-Type': 'application/x-www-form-urlencoded',
		'Referer': 'https://rutracker.org/forum/index.php',
		'Origin': 'https://rutracker.org',
		'Upgrade-Insecure-Requests': '1'
	})
	data = {
		'login_username': user,
		'login_password': password,
		'login': '%E2%F5%EE%E4'
	}
	cookies = {'bb_dev': '1-3'}
	session.post('https://rutracker.org/forum/login.php', data=data, cookies = cookies)
	if 'bb_session' not in str(session.cookies):
		raise Exception('Invalid credentials')	
	
	util.setCookie(session, 'www.rutracker.ru', 'MyLoginInfo', user + '&' + str(time.time()) )
	util.saveCookies(session, pathCookies)
	
	
def getUserDetails(session):	
	try:
		loginInfo = session.cookies._find(name='MyLoginInfo', domain='www.kinopoisk.com').split('&')
		return ({
			'user': loginInfo[0],
			'ts': float(loginInfo[1])
		})
	except:
		return None	
		
	
	
def search (pathCookies, str):
	session = requests.Session()
	session.verify = False
	util.loadCookies(session, pathCookies)
	util.setUserAgent(session, 'chrome')
	url = 'https://rutracker.org/forum/tracker.php'
	dataGet = {
#		'f': '100,101,1102,1120,1214,1235,1359,1363,1531,1576,1666,185,187,189,1900,1936,208,209,2090,2091,2092,2093,2100,212,2198,2199,22,2200,2201,2220,2221,235,2366,242,2459,2540,271,312,313,315,376,387,4,505,521,539,7,721,819,822,842,9,905,911,921,93,930,934,941',
		'nm': str
	}
	dataPost = {
		'o': 10,
		's': 2,
		'oop': 1
	}
	data = BeautifulSoup(session.post (url = url + '?' + urllib.urlencode(dataGet), data = dataPost).content, "html.parser")
	result = []	
	for tag in data.find('tbody').find_all(class_="tCenter"):
		try:
			seeds = tag.find(class_="seedmed").get_text()
		except:
			seeds = '0'
		if seeds == '0':
			continue
		subtag = tag.find(class_="tLink")
		name = subtag.get_text()		
		result.append({
			'id': subtag['data-topic_id'], 	
			'name': name,
			'url': 'https://rutracker.org/forum/dl.php?t=' + subtag['data-topic_id'],
			'seeds': seeds,
			'size': tag.find(class_="tor-size").find('u').get_text()
		})
	return (result)
	
	
def getMagnet(pathCookies, id):
	session = requests.Session()
	session.verify = False
	util.loadCookies(session, pathCookies)
	util.setUserAgent(session, 'chrome')
	data = BeautifulSoup(session.get('https://rutracker.org/forum/viewtopic.php?t=' + id).content, "html.parser")
	magnet = data.find(class_='magnet-link')['href']
	name = data.find(class_='topic-title-' + id).get_text()	
	return(magnet + '&' + urllib.urlencode({'dn': name}))
