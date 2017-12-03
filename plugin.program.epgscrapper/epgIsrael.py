# coding: utf-8

import util
import datetime
from bs4 import BeautifulSoup



def getChannelData(id, days):
	today = datetime.date.today()
	data = []
	s = util.Session()
	url = 'https://www.yes.co.il/content/YesChannelsHandler.ashx'
	params = {
		'action': 'GetDailyShowsByDayAndChannelCode',		
		'dayPartByHalfHour': 0,
		'channelCode': id
	}
	for day in range(0, days):
		theday = today + datetime.timedelta(days=day)
		params['dayValue'] = day
		content = BeautifulSoup(s.get(url=url, params=params).text, "html.parser")
		for tag in content.find_all(class_="text"):	
			pdata = tag.get_text().split(' - ')
			data.append({'time': datetime.datetime(theday.year, theday.month, theday.day, int(pdata[0].split(':')[0]), int(pdata[0].split(':')[1])), 'name': pdata[1]})
	return data

	
def getEPG(days, playlist):
	result = {}
	channels = {
		'CH34': 'קשת',
		'CH36': 'רשת',
		'TV04': 'ערוץ 10',
		'TV67': 'ערוץ 24',
		'TV50': 'ערוץ 9'
	}
	for channel in channels.keys():
		if channels[channel] in playlist:
			result[channels[channel]] = getChannelData(channel,days)
	return result