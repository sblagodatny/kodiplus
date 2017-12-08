# -*- coding: utf-8 -*-

import requests
import urllib
import util
import json
import re
from jsinterp import JSInterpreter
from bs4 import BeautifulSoup
import re
import Cookie
import ast
import urllib2
import google
import urlparse


youtubeUrl = 'https://www.youtube.com/'



itagsVod = ['22','18']
itagsLive = ['95','93']
	
	
def getMyVideos(session):
	result = []
	content = session.get( youtubeUrl + 'my_videos' + '?' + urllib.urlencode({'o': 'U'})).text		
	dummy, i = util.substr ('"VIDEO_LIST_DISPLAY_OBJECT"',':',content)	
	data = json.loads(util.parseBrackets(content, i, ['[',']']))
	for item in data:
		soup = BeautifulSoup(util.unescape(item['html'].decode('unicode_escape')), "html.parser")	
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
	channel = google.getUserDetails(session)['channel']
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
		
		
		
		
def getVideoInfo(session, id, player):		
	headers = {
		'Host': 'www.youtube.com',
		'Connection': 'keep-alive',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
		'Accept': '*/*',
		'DNT': '1',
		'Referer': 'https://www.youtube.com/tv',
		'Accept-Encoding': 'gzip, deflate',
		'Accept-Language': 'en-US,en;q=0.8,de;q=0.6'
	}
	args = player.get("args", {})
	params = {'video_id': id,
		'eurl': 'https://youtube.googleapis.com/v/' + id,
		'ssl_stream': '1',
		'el': 'default',
		'html5': '1',
		'sts': player.get('sts', ''),
		'c': args.get('c', 'WEB'),
		'cver': args.get('cver', '1.20170712'),
		'cplayer': args.get('cplayer', 'UNIPLAYER'),
		'cbr': args.get('cbr', 'Chrome'),
		'cbrver': args.get('cbrver', '53.0.2785.143'),
		'cos': args.get('cos', 'Windows'),
		'cosver': args.get('cosver', '10.0')
	}	
	data = session.get( 'http://www.youtube.com/get_video_info', params=params, headers=headers).text		
	return (dict(urlparse.parse_qsl(data)))

	
def getPlayer(session, id):
	params = {'v': id}
	url = 'https://www.youtube.com/watch'
	content = session.get(url, params=params).text
	dummy, i = util.substr ('ytplayer.config','= ',content)
	player = json.loads(util.parseBrackets(content, i, ['{','}']))
	return player
	
def getCipher(session, player):
	playerJS = session.get( youtubeUrl + player.get("assets", {}).get("js")).text	
	tmp = playerJS
	while True:
		func, i = util.substr('set("signature",','(',tmp)
		if not '.sig' in func:
			break
		if func is None:
			raise Exception ('Unable to find cipher function')
		tmp = tmp[i:]
	jsi = JSInterpreter(playerJS)
	cipherFunction = jsi.extract_function(func)
	return cipherFunction
	
	
def getStreams(id, session):	
	streams = {}
	player = getPlayer(session, id)
	cipher = getCipher(session, player)
	info = getVideoInfo(session, id, player)
	data = info.get('url_encoded_fmt_stream_map', '')
	if len(data) > 5:
		data = data.split(',')
		for i in range(len(data)):
			stream = dict(urlparse.parse_qsl(data[i]))
			url = urllib.unquote(stream['url'])
			if '&signature=' not in url and 's' in stream.keys():
				url = url + '&signature=' + cipher([stream['s']])
			streams.update({stream['itag']: url})		
	else:	
		data = session.get(urllib.unquote(info['hlsvp'])).text.splitlines()
		for i in range (len(data)):
			if data[i].startswith('http'):
				itag, dummy = util.substr("itag/","/",data[i])
				streams.update({itag: data[i]})		
	return streams
	
	
def getDash(id, session):	
	player = getPlayer(session, id)
	cipher = getCipher(session, player)
	info = getVideoInfo(session, id, player)
	dash = urllib.unquote(info.get('dashmpd', ''))
	if '/signature/' not in dash and '/s/' in dash:
		s, i = util.substr('/s/','/',dash)
		signature = cipher([s])
		dash = dash.replace('/s/' + s, '/signature/' + signature)
#	if info.get('live_playback', '0') == '1':
#		dash += '&start_seq=$START_NUMBER$'
	return (dash)
	
