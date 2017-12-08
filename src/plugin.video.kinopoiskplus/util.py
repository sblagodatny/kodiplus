import sys
import cPickle as pickle
import requests
import time
import datetime






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

def fopen(path, mode, xbmc = True):
	if xbmc:
		import xbmcvfs
		return(xbmcvfs.File (path, mode))
	else:
		return(open(path, mode))

def objToFile(obj, path, xbmc = True):
	output = fopen(path, 'w', xbmc)
	pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)
	output.close()
	
def fileToObj(path, xbmc = True):
	input = fopen(path, 'r', xbmc)
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
	def __init__(self, cookiesFolder = '.', xbmc = True):
		requests.Session.__init__(self)	
		requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
		self.verify = False
		self.headers.update({
			'User-Agent': self._userAgent,
			'Accept-Language': 'en-US,en;q=0.8,he;q=0.6,ru;q=0.4',
			'Accept-Encoding': 'gzip, deflate, sdch, br',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
			'Upgrade-Insecure-Requests': '1',
			'Connection': 'keep-alive'
		})
		self.cookiesFolder = cookiesFolder
		self.xbmc = xbmc
		cookies = self.cookies
		self.cookies = fileToObj(cookiesFolder + '/cookies', self.xbmc)
		if self.cookies is None:
			self.cookies = cookies
	def saveCookies(self):
		objToFile(self.cookies, self.cookiesFolder + '/cookies', self.xbmc)
	def download(self, url, path):
		output = fopen(path, 'w', self.xbmc)
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
	

	

