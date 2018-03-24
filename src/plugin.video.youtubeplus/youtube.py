# -*- coding: utf-8 -*-

import util
from bs4 import BeautifulSoup
import json
from jsinterp import JSInterpreter
import urllib
import urllib2
import urlparse


youtubeUrl = 'https://www.youtube.com/'



itagsVideo = ['22','18']
	
	
def getMyVideos(session):
	result = []
	content = session.get( youtubeUrl + 'my_videos' + '?' + urllib.urlencode({'o': 'U'})).text		
	dummy, i = util.substr ('"VIDEO_LIST_DISPLAY_OBJECT"',':',content)	
	data = json.loads(util.parseBrackets(content, i, ['[',']']))
	for item in data:
		soup = BeautifulSoup(util.unescape(item['html'].decode('utf-8')), "html.parser")	
		ptag = soup.find(class_="vm-video-indicators")
		privacy = 'Public'				
		if not ptag.find(class_='vm-unlisted').parent.has_attr('aria-hidden'):
			privacy = 'Private'
		if not ptag.find(class_='vm-private').parent.has_attr('aria-hidden'):
			privacy = 'Private'
		try:
			duration = util.timeStrToSeconds(soup.find(class_="video-time").get_text())
		except:
			duration = ''
		result.append({
			'id': item['id'],
			'name': soup.find(class_="vm-video-title-content").get_text(),		
			'thumb': videoImage(item['id']),			
			'duration': duration,
			'privacy': privacy,
			'user': 'Unknown'			
		})
	return (result)
	
	
def getMyPlaylists(session):
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


def getSavedPlaylists(session):
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


	
def searchVideos(searchStr, session):
	result = []
	content = session.get( youtubeUrl + 'results' + '?' + urllib.urlencode({'search_query': searchStr, 'sp': 'EgIQAVAU'})).text
	dummy, i = util.substr ('"itemSectionRenderer":{"contents"',':',content)
	data = json.loads(util.parseBrackets(content, i, ['[',']']))
	for item in data:
		if 'videoRenderer' not in item.keys():
			continue
		try:
			duration = util.timeStrToSeconds(item['videoRenderer']['lengthText']['simpleText'])
		except:
			duration = ''
		result.append({
			'id': item['videoRenderer']['videoId'], 
			'name': item['videoRenderer']['title']['simpleText'],
			'thumb': item['videoRenderer']['thumbnail']['thumbnails'][0]['url'],
			'duration': duration,
			'privacy': 'Public',
			'user': 'Unknown'
		})
	return (result)

	
def videoImage(id):
	return ('https://i.ytimg.com/vi/' + id + '/hqdefault.jpg')
	
	
def getPlaylistVideos(id, session):
	result = []
	content = session.get( youtubeUrl + 'playlist' + '?' + urllib.urlencode({'list': id})).text
	dummy, i = util.substr ('playlistVideoListRenderer":{"contents"',':',content)
	data = json.loads(util.parseBrackets(content, i, ['[',']']))
	for item in data:
		try:
			name = item['playlistVideoRenderer']['title']['simpleText']
		except:
			continue
		try:
			duration = util.timeStrToSeconds(item['playlistVideoRenderer']['lengthText']['simpleText'])
		except:
			duration = ''
		result.append({
			'id': item['playlistVideoRenderer']['videoId'], 
			'name': name,
			'thumb': item['playlistVideoRenderer']['thumbnail']['thumbnails'][0]['url'],
			'duration': duration,
			'privacy': 'Public',
			'user': 'Unknown'
		})
	return (result)

	
def searchPlaylists(searchStr, session):
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
	
	
def getStreams(id, session):	
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
	return streams

	
