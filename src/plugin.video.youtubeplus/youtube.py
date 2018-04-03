# -*- coding: utf-8 -*-

import util
from bs4 import BeautifulSoup
import json
from jsinterp import JSInterpreter
import urllib
import urllib2
import urlparse
import requests

youtubeUrl = 'https://www.youtube.com/'



itagsVideo = ['22','18']
	
	
def getMyVideos(pathCookies):
	session = requests.Session()
	session.verify = False
	util.loadCookies(session, pathCookies)
	util.setUserAgent(session, 'chrome')	
	result = []
	content = session.get( youtubeUrl + 'my_videos' + '?' + urllib.urlencode({'o': 'U'})).text		
	dummy, i = util.substr ('"VIDEO_LIST_DISPLAY_OBJECT"',':',content)	
	data = json.loads(util.parseBrackets(content, i, ['[',']']))
	for item in data:
		soup = BeautifulSoup(util.unescape(item['html'].decode('utf-8')), "html.parser")	
		ptag = soup.find(class_="vm-video-indicators")	
		content = {
			'id': item['id'],
			'name': soup.find(class_="vm-video-title-content").get_text(),		
			'thumb': videoImage(item['id']),			
			'duration': '',
			'publishedTime': '',
			'viewCount': '',
			'owner': 'You',
			'privacy': 'Public',		
		}
		if not ptag.find(class_='vm-unlisted').parent.has_attr('aria-hidden'):
			content['privacy'] = 'Private'
		if not ptag.find(class_='vm-private').parent.has_attr('aria-hidden'):
			content['privacy'] = 'Private'
		try: 
			content['duration'] = soup.find(class_="video-time").get_text()
		except: 
			continue	
		try: 
			content['publishedTime'] = soup.find(class_='localized-date').get_text().replace(' at','')			
		except: 
			None
		try: 
			content['viewCount'] = soup.find(class_='vm-video-side-view-count').get_text().replace(' views','').replace(' view','').replace("\n",'').replace(' ','')			
		except: 
			None
		
		
		
		result.append(content)
		
	return (result)
	
	
def getMyPlaylists(pathCookies):
	session = requests.Session()
	session.verify = False
	util.loadCookies(session, pathCookies)
	util.setUserAgent(session, 'chrome')	
	result = []
	soup = BeautifulSoup(session.get( youtubeUrl + 'view_all_playlists').text, "html.parser")
	for pltag in soup.find_all(class_="playlist-item"):
		result.append({
			'id': pltag['id'].replace('vm-playlist-',''), 
			'name': pltag.find(class_="vm-video-title-text").get_text(),
			'thumb': 'https://i.ytimg.com/vi/' + pltag.find(class_="vm-video-item-content").find('a')['href'].split('&')[0].replace('/watch?v=','') + '/hqdefault.jpg',			
			'count': pltag.find(class_="video-count-box").get_text().replace('videos','').replace('video','').replace("\n",'').replace(' ',''),
			'privacy': pltag.find(class_="vm-video-privacy")['aria-label'],
			'user': 'Unknown'
		})
	return (result)


def getSavedPlaylists(pathCookies):
	session = requests.Session()
	session.verify = False
	util.loadCookies(session, pathCookies)
	util.setUserAgent(session, 'chrome')	
	result = []
	loginInfo = session.cookies._find(name='MyLoginInfo', domain='www.google.com').split('&')
	channel = loginInfo[1]	
	content = session.get( youtubeUrl + 'channel/' + channel + '/playlists' + '?' + urllib.urlencode({'sort': 'dd', 'view_as': 'subscriber', 'view': '52', 'shelf_id': '0'})).text
	dummy, i = util.substr ('[{"gridRenderer":{"items"',':',content)
	data = json.loads(util.parseBrackets(content, i, ['[',']']))
	for item in data:
		try:
			count = item['gridPlaylistRenderer']['videoCountShortText']['simpleText']
		except:
			count = ''
		result.append({
			'id': item['gridPlaylistRenderer']['playlistId'], 			
			'name': item['gridPlaylistRenderer']['title']['simpleText'],		
			'thumb': item['gridPlaylistRenderer']['thumbnail']['thumbnails'][0]['url'],
			'count': count,
			'privacy': 'Public',
			'user': 'Unknown'
		})
	return (result)


	
def searchVideos(searchStr, pathCookies):
	session = requests.Session()
	session.verify = False
	util.loadCookies(session, pathCookies)
	util.setUserAgent(session, 'chrome')	
	result = []
	content = session.get( youtubeUrl + 'results' + '?' + urllib.urlencode({'search_query': searchStr, 'sp': 'EgIQAVAU'})).text
	dummy, i = util.substr ('"itemSectionRenderer":{"contents"',':',content)
	data = json.loads(util.parseBrackets(content, i, ['[',']']))
	for item in data:
		if 'videoRenderer' not in item.keys():
			continue		
		content = {
			'id': item['videoRenderer']['videoId'], 
			'name': item['videoRenderer']['title']['simpleText'],
#			'thumb': item['videoRenderer']['thumbnail']['thumbnails'][0]['url'],
			'thumb': videoImage(item['videoRenderer']['videoId']),
			'duration': '',
			'publishedTime': '',
			'viewCount': '',
			'owner': '',
			'privacy': 'Public',		
		}
		try: 
			content['duration'] = item['videoRenderer']['lengthText']['simpleText'] 
		except: 
			continue
		try: 
			content['publishedTime'] = item['videoRenderer']['publishedTimeText']['simpleText'] 
		except: 
			None
		try: 
			content['viewCount'] = item['videoRenderer']['viewCountText']['simpleText'].replace(' views','') 
		except: 
			None
		try: 
			content['owner'] = item['videoRenderer']['ownerText']['runs'][0]['text'] 
		except: 
			None
		result.append(content)
	return (result)

	
def videoImage(id):
	return ('https://i.ytimg.com/vi/' + id + '/hqdefault.jpg')
	
	
def getPlaylistVideos(id, pathCookies):
	session = requests.Session()
	session.verify = False
	util.loadCookies(session, pathCookies)
	util.setUserAgent(session, 'chrome')	
	result = []
	content = session.get( youtubeUrl + 'playlist' + '?' + urllib.urlencode({'list': id})).text
	dummy, i = util.substr ('playlistVideoListRenderer":{"contents"',':',content)
	data = json.loads(util.parseBrackets(content, i, ['[',']']))
	for item in data:
		if 'playlistVideoRenderer' not in item.keys():
			continue		
		content = {
			'id': item['playlistVideoRenderer']['videoId'], 
			'name': item['playlistVideoRenderer']['title']['simpleText'],
#			'thumb': item['playlistVideoRenderer']['thumbnail']['thumbnails'][0]['url'],
			'thumb': videoImage(item['playlistVideoRenderer']['videoId']),
			'duration': '',
			'publishedTime': '',
			'viewCount': '',
			'owner': '',
			'privacy': 'Public',		
		}
		try: 
			content['duration'] = item['playlistVideoRenderer']['lengthText']['simpleText'] 
		except: 
			continue
		try: 
			content['owner'] = item['playlistVideoRenderer']['shortBylineText']['runs'][0]['text'] 
		except: 
			None
		result.append(content)	
	return (result)

	
def searchPlaylists(searchStr, pathCookies):
	session = requests.Session()
	session.verify = False
	util.loadCookies(session, pathCookies)
	util.setUserAgent(session, 'chrome')	
	result = []
	content = session.get( youtubeUrl + 'results' + '?' + urllib.urlencode({'search_query': searchStr, 'sp': 'EgIQA1AU'})).text
	dummy, i = util.substr ('"itemSectionRenderer":{"contents"',':',content)
	data = json.loads(util.parseBrackets(content, i, ['[',']']))
	for item in data:
		if 'playlistRenderer' not in item.keys():
			continue
		result.append({
			'id': item['playlistRenderer']['playlistId'], 			
			'name': item['playlistRenderer']['title']['simpleText'],		
			'thumb': item['playlistRenderer']['thumbnails'][0]['thumbnails'][0]['url'],
			'count': item['playlistRenderer']['videoCount'],
			'privacy': 'Public',
			'user': 'Unknown'
		})
	return (result)
		

	
def getPlayer(session, id):
	params = {'v': id}
	url = 'https://www.youtube.com/watch'
	content = session.get(url, params=params).text
	dummy, i = util.substr ('ytplayer.config','= ',content)
	player = json.loads(util.parseBrackets(content, i, ['{','}']))
	return player
	
def getCipher(session, player):
	playerJS = session.get( youtubeUrl + player.get("assets", {}).get("js")).text	
	function, dummy = util.substr ('"signature":"sig";','(',playerJS)
	function = function.split('=')[1]
	jsi = JSInterpreter(playerJS)
	return jsi.extract_function(function)
	
	
def getStreams(id, pathCookies):	
	session = requests.Session()
	session.verify = False
	util.loadCookies(session, pathCookies)
	util.setUserAgent(session, 'chrome')	
	streams = {}
	player = getPlayer(session, id)
	cipher = getCipher(session, player)
	data = player.get("args", {}).get("url_encoded_fmt_stream_map","")
	if len(data) > 5:
		data = data.split(',')
		for i in range(len(data)):
			stream = dict(urlparse.parse_qsl(data[i]))
			url = urllib.unquote(stream['url'])
			if '&signature=' not in url and 's' in stream.keys():
				url = url + '&signature=' + cipher([stream['s']])
			streams.update({stream['itag']: url})
	cookies = session.cookies.get_dict(domain='.youtube.com')
	return streams, cookies

	
