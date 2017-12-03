# coding: utf-8

import util
import urllib
from bs4 import BeautifulSoup



_ruTrackerUrl = 'http://rutracker.org/'

	
def login(session, user, password):
	try:
		headers = session.headers
		headers.update ({
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
		session.post('https://rutracker.org/forum/login.php', data=data, headers=headers, cookies = cookies)
		if 'bb_session' not in str(session.cookies):
			raise Exception('Invalid credentials')	
	except Exception as e:
		raise Exception('Unable to login to Rutracker: ' + str(e))
	args = {
			'domain': 'www.rutracker.ru',
			'expires': None,
			'path': '/',
			'version':0
		}
	session.cookies.set(name='MyLoginInfo',value=user, **args)
	session.saveCookies()


def getUserDetails(session):	
	try:
		loginInfo = session.cookies._find(name='MyLoginInfo', domain='www.rutracker.ru')
		return ({'user': loginInfo})
	except:
		return None
	
	
def loginVerify (session, user, password):
	loginInfo = getUserDetails(session)
	if loginInfo is not None:
		if loginInfo['user'] == user:
			return
	login(session,user,password)	


	
def verifyStrictExpr(name, strict):
	if strict is None:
		return True
	for se in strict:
		found = False
		for s in se:
			if s.replace('ё','е') in name.replace('ё','е'):
				found = True
		if not found:
			return False
	return True
	
	
def search (session, str, strict=None):
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
	startvalues=['0']
	for tag in data.find(class_='bottom_info').find_all(class_='pg'):
		value = tag['href'].split('start=')[1].split('"')[0]
		if value not in startvalues:
			startvalues.append(value)
	
	result = []	
	for startvalue in startvalues:
		dataGet['start'] = startvalue
		data = BeautifulSoup(session.post (url = url + '?' + urllib.urlencode(dataGet), data = dataPost).content, "html.parser")
		for tag in data.find('tbody').find_all(class_="tCenter"):
			try:
				seeds = tag.find(class_="seedmed").get_text()
			except:
				seeds = '0'
			if seeds == '0':
				continue
			subtag = tag.find(class_="tLink")
			name = subtag.get_text()
			if not verifyStrictExpr(name, strict):
				continue			
			result.append({
				'id': subtag['data-topic_id'], 	
				'name': name,
				'url': 'https://rutracker.org/forum/dl.php?t=' + subtag['data-topic_id'],
				'seeds': seeds,
				'size': tag.find(class_="tor-size").find('u').get_text()
			})
			
	return (result)
	
	
def getMagnet(session, id):
	data = BeautifulSoup(session.get('https://rutracker.org/forum/viewtopic.php?t=' + id).content, "html.parser")
	magnet = data.find(class_='magnet-link')['href']
	name = data.find(class_='topic-title-' + id).get_text()	
	return(magnet + '&' + urllib.urlencode({'dn': name}))
