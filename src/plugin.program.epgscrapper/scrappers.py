# coding: utf-8

import util
import datetime
import time
import requests
from bs4 import BeautifulSoup
import json
from pytz import timezone


def getEpgYes(id, days):
	tz = datetime.datetime.now(timezone('Asia/Jerusalem')).tzinfo
	today = datetime.date.today()
	result = []
	s = requests.Session()
	url = 'https://www.yes.co.il/content/YesChannelsHandler.ashx'
	params = {
		'action': 'GetDailyShowsByDayAndChannelCode',		
		'dayPartByHalfHour': 0,
		'channelCode': id
	}
	for day in range(0, days):
		programs = []
		theday = today + datetime.timedelta(days=day)
		params['dayValue'] = day
		content = BeautifulSoup(s.get(url=url, params=params).text, "html.parser")
		for tag in content.find_all(class_="text"):	
			pdata = tag.get_text().split(' - ')
			start = datetime.datetime(year=theday.year, month=theday.month, day=theday.day, hour=int(pdata[0].split(':')[0]), minute=int(pdata[0].split(':')[1]), tzinfo=tz)
			programs.append({
				'start': start, 
				'title': pdata[1],
				'description': ''
			})
		for i in range (0, len(programs)-1):
			programs[i]['stop'] = programs[i+1]['start']
		programs[-1]['stop'] = datetime.datetime(year=theday.year, month=theday.month, day=theday.day, hour=23, minute=59, tzinfo=tz)
		result.extend(programs)
	return result
	


	
def getEpgYandex(id, days):
#	tz = datetime.datetime.now(timezone('Europe/Moscow')).tzinfo
	tz = datetime.datetime.now(timezone('Asia/Jerusalem')).tzinfo
	today = datetime.date.today()
	programs = []
	s = requests.Session()
	url = 'https://tv.yandex.ru/213/channels/' + id
	for day in range(0, days):
		theday = today + datetime.timedelta(days=day)
		params = {'date': datetime.datetime.strftime(theday,'%Y-%m-%d')}	
		content = s.get(url=url, params=params).text
		dummy, i = util.substr ('"events"',':',content)	
		data = json.loads(util.parseBrackets(content, i, ['[',']']))
		for pdata in data:	
			start = datetime.datetime(year=int(pdata['start'][0:4]), month=int(pdata['start'][5:7]), day=int(pdata['start'][8:10]), hour=int(pdata['start'][11:13]), minute=int(pdata['start'][14:16]), tzinfo=tz)
			stop = datetime.datetime(year=int(pdata['finish'][0:4]), month=int(pdata['finish'][5:7]), day=int(pdata['finish'][8:10]), hour=int(pdata['finish'][11:13]), minute=int(pdata['finish'][14:16]), tzinfo=tz)
			program = {
				'start': start,
				'stop': stop,
				'title': pdata['program']['title'],
				'description': ''
			}
			if 'episode' in pdata:
				if 'title' in pdata['episode']:
					if pdata['episode']['title'] != program['title']:
						program['title'] = program['title'] + ', ' + pdata['episode']['title']
			if 'description' in pdata['program']:
				program['description'] = pdata['program']['description'].replace ("\n","")
			programs.append(program)
	return programs
