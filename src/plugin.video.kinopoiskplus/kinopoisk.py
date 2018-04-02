# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import util
import json
import re
import urllib
import time
import sys
import json
import kinopoiskplus


_genres = {
	'Комедия': '6',
	'Боевик': '3,13,16,19',
	'Приключения': '10',
	'Детектив': '17',
	'Фантастика': '2',
	'Детский': '456'	
}

_countries = {
	'СНГ': '2,13,2,13,62',
	'США': '1',
	'Европа': '11,3,15,14,8',
	'Индия': '29'
}		



def getThumb(id):
	return 'https://www.kinopoisk.ru/images/sm_film/' + id + '.jpg'
	
def getPoster(id):
	return 'https://www.kinopoisk.ru/images/film_big/' + id + '.jpg'
	
def searchByTitle(pathCookies, title, contentType='Movie'):
	session = requests.Session()
	session.verify = False
	util.loadCookies(session, pathCookies)
	util.setUserAgent(session, 'chrome')	
	url = 'https://www.kinopoisk.ru/s/type/film'
	url = url + '/find/' + title
	if contentType == 'serial':
		url = url + '/m_act[type]/serial'
	url = url + '/list/1/order/relevant/perpage/10'
	data = BeautifulSoup(session.get(url).content, "html.parser")
	result = []	
	for tag in data.find_all(class_="element"):		
		try:
			myrating = tag.find(class_='my_vote').get_text()
		except:
			myrating = ''
		try:
			year = tag.find(class_="year").get_text()
		except:
			continue
		result.append({
			'id': tag.find(class_="info").find('a')['data-id'],
			'name': cleanseName(tag.find(class_="name").find('a').get_text()),
			'year': year,
			'myrating': myrating
		})
	return result
	
	
def searchByParams(pathCookies, contentType='Movie', hideWatched=True, hideInFolders = False, genre=None, years=None, countries=None):
	session = requests.Session()
	session.verify = False
	util.loadCookies(session, pathCookies)
	util.setUserAgent(session, 'chrome')	
	genreExclude = '12,1747,15,9,28,25,26,1751'
	url = 'https://www.kinopoisk.ru/top/navigator'
	if contentType is not None:
		if contentType == 'movie':
			url = url + '/m_act[is_film]/on'
		if contentType == 'serial':
			url = url + '/m_act[is_serial]/on'
	if hideWatched:
		url = url + '/m_act[hide]/on'
	if hideInFolders:
		sf = ''
		for folderId in getFolders(session).keys():
			sf = sf + folderId + ';'
		url = url + '/m_act[folders]/' + sf
	if genre is not None:
		url = url + '/m_act[genre]/' + genre + '/m_act[genre_or]/on'	
	url = url + '/m_act[egenre]/' + genreExclude
	if years is not None:
		url = url + '/m_act[years]/' + years
	if countries is not None:
		url = url + '/m_act[country]/' + countries + '/m_act[country_or]/on'
	url = url + '/order/rating/perpage/10/#results'	
	data = BeautifulSoup(session.get(url).content, "html.parser")
	result = []
	for tag in data.find_all(class_="item _NO_HIGHLIGHT_"):
		result.append({
			'id': tag['id'].replace('tr_',''),
			'name': cleanseName(tag.find(class_="name").find('a').get_text()),
			'year': tag.find(class_="name").find('span').get_text().split('(')[-1].split(')')[0],
			'myrating': tag.find(class_='myVote').find('p').get_text()
		})
	return (result)	
	
			
	
def setWatched(pathCookies,id,state,vote='7'):		
	session = requests.Session()
	session.verify = False
	util.loadCookies(session, pathCookies)
	util.setUserAgent(session, 'chrome')
	session.headers['X-Requested-With'] = 'XMLHttpRequest'
	xsrftoken = kinopoiskplus.getUserDetails(session)['xsrftoken']
	data = {
		'token': xsrftoken,
		'id_film': id
#		'c': uc
	}		
	if state:
		data.update({'act': 'add'})
		reply = session.get("https://www.kinopoisk.ru/handler_vote.php" + '?' + urllib.urlencode(data))
		if reply.status_code != 200:
			raise Exception ('Unable to update Kinopoisk')
		del data['act']
		data.update({'vote': vote})
		reply = session.get("https://www.kinopoisk.ru/handler_vote.php" + '?' + urllib.urlencode(data))
		if reply.status_code != 200:
			raise Exception ('Unable to update Kinopoisk')
	else:
		data.update({'act': 'kill_vote'})
		reply = session.get("https://www.kinopoisk.ru/handler_vote.php" + '?' + urllib.urlencode(data))
		if reply.status_code != 200:
			raise Exception ('Unable to update Kinopoisk')
		data.update({'act': 'delete'})
		reply = session.get("https://www.kinopoisk.ru/handler_vote.php" + '?' + urllib.urlencode(data))
		if reply.status_code != 200:
			raise Exception ('Unable to update Kinopoisk')

		
def getDetails(pathCookies, id):
	session = requests.Session()
	session.verify = False
	util.loadCookies(session, pathCookies)
	util.setUserAgent(session, 'chrome')
	session.headers.update ({
		'Referer': 'https://www.kinopoisk.ru/',
		'Accept-Language': 'en-US,en;q=0.8,he;q=0.6,ru;q=0.4',
		'Accept-Encoding': 'gzip, deflate, sdch, br',
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		'Upgrade-Insecure-Requests': '1',
		'Connection': 'keep-alive'
	})
	url = 'https://www.kinopoisk.ru/film/' + id + '/'
	data = BeautifulSoup(session.get(url).content, "html.parser")
	name = cleanseName(data.find(class_='moviename-big').get_text())
	nameOrig = data.find('span', {'itemprop':'alternativeHeadline'}).get_text()
	description = data.find(class_='film-synopsys').get_text()
	rating = data.find(class_='rating_ball').get_text()
	info = data.find(class_='info')
	country = []	
	try:
		countryTags = info.find(text='страна').find_next()
		for countryTag in countryTags.find_all('a'):
			country.append(countryTag.get_text())
	except:
		None
	genre = []
	try:
		genreTags = info.find(text='жанр').find_next().find('span')
		for genreTag in genreTags.find_all('a'):
			genre.append(genreTag.get_text())
	except:
		None
	year = info.find(text='год').find_next().find('a').get_text()
	myrating, dummy = util.substr('myVote:',',',str(data))
	if myrating is None:
		myrating = ''
	result = {
		'description': description,
		'rating' : rating,
		'myrating': myrating,
		'country': country,
		'year': year,
		'genre': genre,
		'name': name,
		'nameOrig': nameOrig,
		'directors': getCast(session, id, 'director'),
		'actors': getCast(session, id, 'actor')
	}
	if isSeries(name):
		seasons = 1
		try:
			seasons = int(info.find(text='год').find_next().find(class_='all').get_text().split(' ')[0].replace('(',''))		
		except:
			None
		result['seasons'] = seasons
	return result
	
	
def getCast(session, id, role):
	data = BeautifulSoup(session.get('https://www.kinopoisk.ru/film/' + id + '/cast/who_is/' + role + '/').content, "html.parser")
	result = []
	for tag in data.find_all(class_='actorInfo'):
		person = tag.find(class_='name').find('a').get_text()
		photo = 'https://www.kinopoisk.ru/' + tag.find(class_='photo').find('img')['title']
		result.append({'name': person, 'role': role, 'thumbnail': photo}) 
	return result
	
	
	
	
	
def manageFolders(pathCookies,id,folders):	
	session = requests.Session()
	session.verify = False
	util.loadCookies(session, pathCookies)
	util.setUserAgent(session, 'chrome')
	session.headers.update({
		'Accept': 'application/json, text/javascript, */*; q=0.01',
		'X-Requested-With': 'XMLHttpRequest'
	})
	xsrftoken = kinopoiskplus.getUserDetails(session)['xsrftoken']
	for folder in folders:
		if folder['assigned']:
			data = {
				'token': xsrftoken,
				'id_film': id,
				'mode': 'add_film', 
				'to_folder': folder['id']
			}
		else:
			data = {
				'token': xsrftoken,
				'id_film': id,
				'mode': 'del_film', 
				'from_folder': folder['id']
			}
		session.get("https://www.kinopoisk.ru/handler_mustsee_ajax.php" + '?' + urllib.urlencode(data)).content
	
	
def getFolders(pathCookies):
	session = requests.Session()
	session.verify = False
	util.loadCookies(session, pathCookies)
	util.setUserAgent(session, 'chrome')
	session.headers.update ({
		'Referer': 'https://www.kinopoisk.ru/mykp/edit_main/'
	})
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
	
	
def getItemFolders(pathCookies, id):
	session = requests.Session()
	session.verify = False
	util.loadCookies(session, pathCookies)
	util.setUserAgent(session, 'chrome')
	session.headers.update ({
		'Referer': 'https://www.kinopoisk.ru/'
	})
	data = session.get('https://www.kinopoisk.ru/film/' + id + '/').content
	data, dummy = util.substr ("var myMoviesData = ",";",data)
	data = json.loads(data)	
	objfolders = data['objFolders'].values()[0].keys()
	result = []
	for folder in data['folders']:
		result.append({
			'id': folder['id'],
			'name': folder['name'],
			'assigned': folder['id'] in objfolders
		})
	return result	
	
	
def getFolderContent(pathCookies, folder):
	session = requests.Session()
	session.verify = False
	util.loadCookies(session, pathCookies)
	util.setUserAgent(session, 'chrome')
	session.headers.update ({
		'Referer': 'https://www.kinopoisk.ru/mykp/movies/'
	})
	data = BeautifulSoup(session.get('https://www.kinopoisk.ru/mykp/movies/list/type/' + folder + '/').content, "html.parser").find('ul',{'id': 'itemList'})
	result = []
	for tag in data.find_all('li'):	
		result.append({
			'id': tag['data-id'],
			'name': cleanseName(tag.find(class_='name').get_text()),
			'year': tag.find(class_='info').find('span').get_text().split('(')[-1].split(')')[0],
			'myrating': tag.find(class_='vote_widget').find_next().get_text().split("rating: '")[1].split("'")[0]
		})		
	return result
	
	
def isSeries(name):
	if '(сериал' in name:
		return True
	return False
	
	
def cleanseName(name):
	result = name
	result = result.replace(' (видео)','')
	result = result.replace(' (ТВ)','')
	result = result.replace('(мини-сериал','(сериал')
	return result