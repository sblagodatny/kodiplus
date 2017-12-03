import requests
import json
import urllib

def resolve(params):
	plurl = '/hls/live/512033/CH2LIVE_HIGH/index.m3u8'
	url = 'https://mass.mako.co.il/ClicksStatistics/entitlementsServicesV2.jsp'
	params = {
		'et': 'gt',
		'lp': plurl,
		'rv': 'AKAMAI',
		'dv': '6540b8dcb64fd310VgnVCM2000002a0c10acRCRD'
	}
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
		'Referer': 'https://www.mako.co.il/mako-vod-live-tv/VOD-6540b8dcb64fd31006.htm'
	}
	s = requests.Session()
	data = json.loads(s.get(url=url, params=params, headers=headers).text)
	ticket = data['tickets'][0]['ticket']
	
	url = 'https://keshethlslive-i.akamaihd.net' + plurl + '?' + ticket
	return url

