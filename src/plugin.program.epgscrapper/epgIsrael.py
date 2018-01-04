# coding: utf-8

import util
import datetime
import time
from bs4 import BeautifulSoup

tzOffsetIsrael = 2 * 3600

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
			data.append({
				'time': datetime.datetime(
					year = theday.year, 
					month = theday.month, 
					day = theday.day, 
					hour = int(pdata[0].split(':')[0]), 
					minute = int(pdata[0].split(':')[1]),
					tzinfo = util.timezone(tzOffsetIsrael)
				), 
				'name': pdata[1]
			})
	return data

	
def getEPG(days):
	result = {}
	channels = {
		'CH34': 'קשת',
		'CH36': 'רשת',
		'TV04': 'ערוץ 10',
		'TV50': 'ערוץ 9'
	}
	for channel in channels.keys():
		result[channels[channel]] = getChannelData(channel,days)
	return result