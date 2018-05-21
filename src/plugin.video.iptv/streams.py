def getKeshetStream():
	import requests
	import json
	plurl = '/hls/live/512033/CH2LIVE_HIGH/index.m3u8'
	url = 'https://mass.mako.co.il/ClicksStatistics/entitlementsServicesV2.jsp'
	params = {
		'et': 'gt',
		'lp': plurl,
		'rv': 'AKAMAI',
		'dv': '6540b8dcb64fd310VgnVCM2000002a0c10acRCRD'
	}
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0',
		'Referer': 'https://www.mako.co.il/mako-vod-live-tv/VOD-6540b8dcb64fd31006.htm'
	}
	s = requests.Session()
	s.verify = False
	data = json.loads(s.get(url=url, params=params, headers=headers).text)
	ticket = data['tickets'][0]['ticket']
	url = 'https://keshethlslive-i.akamaihd.net' + plurl + '?' + ticket
	data = s.get(url=url, headers=headers)
	cookies = s.cookies.get_dict()
	headers.update({'Cookie': "; ".join([str(x)+"="+str(y) for x,y in cookies.items()])}),
	url = 'https://keshethlslive-i.akamaihd.net/hls/live/512033-b/CH2LIVE_HIGH/index_2200.m3u8'	
	return url, headers

	
def getReshetStream():
	url = 'http://besttv10.aoslive.it.best-tv.com/reshet/studio/index_4.m3u8'
	headers = {'Referer':'http://reshet.tv/live/'}
	return (url, headers)