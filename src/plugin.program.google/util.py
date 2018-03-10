import sys
import cPickle as pickle
import requests
import time
import datetime
import xbmcvfs
from bs4 import BeautifulSoup







### String utilities ###

def setDefaultEncoding(encoding='utf-8'):
	reload(sys)  
	sys.setdefaultencoding(encoding)

def substr(strStart, strStop, content):	
	i1=content.find(strStart)
	if i1 == -1: 
		return (None,None)
	i2 = content.find(strStop, i1+len(strStart))
	if i2 == -1: 
		return (None, None)
	return ( content[i1:][:i2-i1].replace(strStart,""), i2 + len(strStop) )

def parseBrackets(html, i, br):
	html = html[i:]
	brackets = 0
	for i, ch in enumerate(html):
		if ch == br[0]:
			brackets += 1
		elif ch == br[1]:
			brackets -= 1
			if brackets == 0:
				break
	return (html[:i + 1])

def escape(str):
    return (str
        .replace("&", "&amp;")
		.replace("<", "&lt;")
		.replace(">", "&gt;")
        .replace("'", "&#39;")
		.replace('"', "&quot;")
		.replace('/', '\/')
        )
		
def unescape(str):
    return (str
        .replace("&amp;","&")
		.replace("&lt;","<")
		.replace("&gt;",">")
        .replace("&#39;","'")
		.replace("&quot;",'"')
		.replace("\/",'/')
        )		
		
	
def timeStrToSeconds (str):
	format = '%H:%M:%S'
	if len(str.split(':')) == 2:
		format = '%M:%S'	
	x = time.strptime(str,format)
	return (datetime.timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec).total_seconds())		

	
def strToBool(str):
	if str.lower() == 'true':
		return True
	if str.lower() == 'false':
		return False
	return None	

def nvl (value, nullvalue):
	if value is None:
		return nullvalue
	return value
		
def nvls(str, nullvalue):
	if str is None:
		return nullvalue
	if len(str) == 0:
		return nullvalue
	return str
	
	
def color(str, color):
	return '[COLOR ' + color + ']' + str + '[/COLOR]'
	
def bold(str):
	return '[B]' + str + '[/B]'
	
	
	
### File utilities ###	
def objToFile(obj, path):
	output = xbmcvfs.File (path, 'w')
	pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)
	output.close()
	
def fileToObj(path):
	input = xbmcvfs.File (path, 'r')
	try:
		obj = pickle.loads(input.read())
	except:
		input.close()
		return None
	input.close()
	return obj

def fileName(path):
	if '/' in path:
		return path.split('/')[-1]
	else:
		return path
	
def fileExt(path):
	if '.' in path:
		return path.split('.')[-1]
	else:
		return ''	
	

### Dict utilities ###
	
def firstMatch(keysToMatch, keys):
	for key in keysToMatch:
		if key in keys:
			return key
	return None
	
def findValue(d, value):
	for key, val in d:
		if val == value:
			return key
	return None

def nvld(data, key, nullvalue):
	if key in data.keys():
		return(data[key])
	return nullvalue


	
### List utilities ###

def sort(list):
	reply = list
	reply.sort()
	return reply

def listToStr(list, delimiter):		
	result = ''
	isFirst =  True
	for value in list:
		if isFirst:
			result = value
			isFirst = False
		else:
			result = result + delimiter + value
	return result	

	
### HTTP Utilities ###	
	
class Session (requests.Session):
	_userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
	def __init__(self, cookiesFolder = '.'):
		requests.Session.__init__(self)	
		requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
		self.verify = False
		self.headers.update({
			'User-Agent': self._userAgent,
		})
		self.cookiesFolder = cookiesFolder
		cookies = self.cookies
		self.cookies = fileToObj(cookiesFolder + '/cookies')
		if self.cookies is None:
			self.cookies = cookies
	def saveCookies(self):
		objToFile(self.cookies, self.cookiesFolder + '/cookies')
	def download(self, url, path):
		output = fopen(path, 'w')
		r = self.get(url)
		for chunk in r.iter_content(chunk_size=1024): 
			if chunk:
				output.write(chunk)
		output.close()
	def setCookie(self, domain, name, value, doSave = False):
		args = {
			'domain': domain,
			'expires': None,
			'path': '/',
			'version':0
		}
		self.cookies.set(name=name, value=value, **args)
		if doSave:
			self.saveCookies()

		
def urldecode(params):	
	result = {}
	for kv in params.split("&"):
		key, value = kv.split("=")
		result.update({key: value})	
	return (result)
	
def urlencode(params):
	result = ''
	for key in params.keys():
		result = result + key + '=' + params[key] + '&'
	return(result[:-1])
	

	
### Date Utilities ###
class timezone(datetime.tzinfo):
	_offset = None
	_dst = None
	def __init__(self, seconds):
		self._offset = datetime.timedelta(seconds = seconds)
		self._dst = datetime.timedelta(0)
	def utcoffset(self, dt):
		return self._offset
	def dst(self, dt):
		return self._dst

def strToDateTime(str):
	return datetime.datetime(year=int(str[0:4]), month=int(str[4:6]), day=int(str[6:8]), hour=int(str[8:10]), minute=int(str[10:12]), tzinfo=timezone(int(str[15:18]) * 3600) )

def now():
	offset = 2
	str = datetime.datetime.strftime(datetime.datetime.now(),'%Y%m%d%H%M')
	return datetime.datetime(year=int(str[0:4]), month=int(str[4:6]), day=int(str[6:8]), hour=int(str[8:10]), minute=int(str[10:12]), tzinfo=timezone(offset * 3600) )

### Other ###
def m3uChannels(m3uFile):	
	channels = []
	f = xbmcvfs.File (m3uFile, 'r')
	data = f.read().splitlines()
	for i in range(0, len(data)):
		if data[i].startswith('#EXTINF'):
			channel = {
				'name': data[i].split(',')[1],
				'url': data[i+1]
			}
			try:
				channel.update({'tvg_id': data[i].split('tvg-id="')[1].split('"')[0]})
			except:
				None
			try:				
				channel.update({'tvg_logo': data[i].split('tvg-logo="')[1].split('"')[0]})
			except:
				None
			try:				
				channel.update({'tvg_shift': data[i].split('tvg-shift="')[1].split('"')[0]})
			except:
				None
			try:				
				channel.update({'archive': data[i].split('archive="')[1].split('"')[0]})
			except:
				None
			channels.append(channel)
	f.close()
	return channels


def xmltvCurrentPrograms(channels, epgFile):
	tvg_shift = {}
	for channel in channels:
		if 'tvg_shift' in channel.keys():
			tvg_shift.update({channel['tvg_id']: channel['tvg_shift']})
	try:
		epg = {}
		f = xbmcvfs.File (epgFile, 'r')
		data = f.read()
		f.close()
		data = BeautifulSoup(data, "html.parser")
		n = now()
		for program in data.find_all('programme'):
			start = strToDateTime(program['start'])
			stop = strToDateTime(program['stop'])
			if program['channel'] in tvg_shift.keys():
				start = start + datetime.timedelta(hours=int(tvg_shift[program['channel']]))
				stop = stop + datetime.timedelta(hours=int(tvg_shift[program['channel']]))			
			if n >= start and n < stop:
				epg.update({
					program['channel']: {'title': program.find('title').get_text(), 'description': program.find('desc').get_text(), 'remaining': stop-n}
				})	
		return epg
	except:
		raise
		return None