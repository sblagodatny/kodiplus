# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import util
import json
import re
import urllib
import time
import sys

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
	
def searchByTitle(session, title, contentType='Movie', years=None):
	url = 'https://www.kinopoisk.ru/s/type/film'
	url = url + '/find/' + title
	if contentType is not None:
		if contentType == 'serial':
			url = url + '/m_act[type]/serial'
	if years is not None:
		from_year = years.split(':')[0]
		to_year = years.split(':')[1]
		if from_year:
			url = url + '/m_act[from_year]/' + from_year
		if to_year:
			url = url + '/m_act[to_year]/' + to_year		
	url = url + '/list/1/order/relevant/perpage/10'
	data = BeautifulSoup(session.get(url).content, "html.parser")
	result = []	
	for tag in data.find_all(class_="element"):	
		subtag = tag.find(class_="info").find('a')
		id = subtag['data-id']		
		result.append(id)
	return result
	
	
def searchByParams(session, contentType='Movie', hideWatched=True, hideInFolders = False, genre=None, years=None, countries=None):
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
		id = tag['id'].replace('tr_','')
		result.append(id)	
	return (result)	
	
	
def setWatched(session,id,state,vote='7'):
	def validate(s):
		if s.lower() != 'ok':
			raise Exception(s)	
			
	data = session.get('https://www.kinopoisk.ru/film/' + id + '/').content
	uc, dummy = util.substr("user_code:'","'",data)
	xsrftoken, dummy = util.substr ("xsrftoken = '","'",data)
	
	data = {
		'token': xsrftoken,
		'id_film': id,
		'c': uc
	}		
	if state:
		data.update({'act': 'add'})
		session.get("https://www.kinopoisk.ru/handler_vote.php" + '?' + urllib.urlencode(data)).content
		del data['act']
		data.update({'vote': vote})
		validate(session.get("https://www.kinopoisk.ru/handler_vote.php" + '?' + urllib.urlencode(data)).content)
	else:
		data.update({'act': 'kill_vote'})
		session.get("https://www.kinopoisk.ru/handler_vote.php" + '?' + urllib.urlencode(data)).content
		data.update({'act': 'delete'})
		validate(session.get("https://www.kinopoisk.ru/handler_vote.php" + '?' + urllib.urlencode(data)).content)

		
def getDetails(session, id):
	headers = session.headers
	session.headers.update ({
		'Referer': 'https://www.kinopoisk.ru/'
	})
	data = BeautifulSoup(session.get('https://www.kinopoisk.ru/film/' + id + '/').content, "html.parser")
	try:
		name = data.find(class_='moviename-big').get_text()
		if ' (' in name:
			name = name.split(' (')[0]
	except:
		name = ''			
	try:
		nameOrig = data.find('span', {'itemprop':'alternativeHeadline'}).get_text()
		if len(nameOrig ) < 2:
			raise
	except:
		nameOrig = None		
	try:
		description = data.find(class_='film-synopsys').get_text()
	except:
		description = ''
	try:
		rating = data.find(class_='rating_ball').get_text()
	except:
		rating = ''	
		
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

	try:
		year = int(info.find(text='год').find_next().find('a').get_text())
	except:
		year = 0	
		
	seasons = None
	seasonsFinal = True
	try:
		t = data.find(class_='moviename-big').find('span').prettify()
		if 'сериал' in t or 'мини-сериал' in t:
			seasons = 1
		if '...' in t:
			seasonsFinal = False
	except:
		None		
	if seasons != 0:
		try:
			seasons = int(info.find(text='год').find_next().find(class_='all').get_text().split(' ')[0].replace('(',''))		
		except:
			None

	
	myrating, dummy = util.substr('myVote:',',',str(data))
	
#	assignedFolders = []
#	try:
#		data = str(data)
#		dummy, i = util.substr ('myMoviesData','= ',data)
#		data = json.loads(util.parseBrackets(data, i, ['{','}']))
#		for dummy,folders in data['objFolders'].items():
#			for folder in folders:
#				assignedFolders.append(folder)
#			break
#	except:
#		None
		
	result = {
		'description': description,
		'rating' : rating,
		'country': country,
		'year': year,
		'genre': genre,
		'name': name,
		'directors': getCast(session, id, 'director'),
		'actors': getCast(session, id, 'actor')
	}
	if seasons is not None:
		result.update({'seasons': seasons, 'seasonsFinal': seasonsFinal})
	if myrating is not None:	
		result.update({'myrating': myrating})
	if nameOrig is not None:
		result.update({'nameOrig': nameOrig})
	
	session.headers = headers
	return result
	
	
def getCast(session, id, role):
	data = BeautifulSoup(session.get('https://www.kinopoisk.ru/film/' + id + '/cast/who_is/' + role + '/').content, "html.parser")
	result = []
	for tag in data.find_all(class_='actorInfo'):
		person = tag.find(class_='name').find('a').get_text()
		photo = 'https://www.kinopoisk.ru/' + tag.find(class_='photo').find('img')['title']
		result.append({'name': person, 'role': role, 'thumbnail': photo}) 
	return result
	
	
	
	
	
def assignToFolder(session,id, folder,state):
	def validate(s):
		if 'ok' not in s.lower():
			raise Exception(s)	
	
	data = session.get('https://www.kinopoisk.ru/film/' + id + '/').content
	xsrftoken, dummy = util.substr ("xsrftoken = '","'",data)
	
	data = {
		'token': xsrftoken,
		'id_film': id,
	}		
	headers = session.headers
	session.headers.update({
		'Accept': 'application/json, text/javascript, */*; q=0.01',
		'X-Requested-With': 'XMLHttpRequest'
	})
	if state:
		data.update({'mode': 'add_film', 'to_folder': folder})
		validate(session.get("https://www.kinopoisk.ru/handler_mustsee_ajax.php" + '?' + urllib.urlencode(data)).content)
		
	else:
		data.update({'mode': 'del_film', 'from_folder': folder})
		validate(session.get("https://www.kinopoisk.ru/handler_mustsee_ajax.php" + '?' + urllib.urlencode(data)).content)
	session.headers = headers
	
def getFolders(session):
	headers = session.headers
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
	session.headers = headers
	return result
	
	
def getFolderContent(session, folder):
	headers = session.headers
	session.headers.update ({
		'Referer': 'https://www.kinopoisk.ru/mykp/movies/'
	})
	data = BeautifulSoup(session.get('https://www.kinopoisk.ru/mykp/movies/list/type/' + folder + '/').content, "html.parser").find('ul',{'id': 'itemList'})
	result = []
	for tag in data.find_all('li'):	
		id = tag['data-id']
		result.append(id)		
	session.headers = headers
	return result
	
