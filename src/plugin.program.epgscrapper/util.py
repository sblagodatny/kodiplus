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
	

	
### XMLTV Utilites ###


def xmltvWriteMultiple(epgs, file):
	idChannel = 1
	idProgram = 1
	f = fopen(file, 'w')
	f.write('<?xml version="1.0" encoding="utf-8"?>' + "\n")
	f.write('<!DOCTYPE tv SYSTEM "http://xmltv.cvs.sourceforge.net/viewvc/xmltv/xmltv/xmltv.dtd">' + "\n")
	f.write('<tv>' + "\n")
	for epg in epgs:
		for channel in epg.keys():
			f.write('<channel id="' + str(idChannel) + '" ><display-name>' + channel.encode('utf-8') + '</display-name></channel>' + "\n")
			for i in range (0, len(epg[channel])-1):
				program = epg[channel][i]
				start = datetime.datetime.strftime(program['time'],'%Y%m%d%H%M%S %z')
				nextprogram = epg[channel][i+1]				
				stop = datetime.datetime.strftime(nextprogram['time'],'%Y%m%d%H%M%S %z')
				f.write('<programme id="' + str(idProgram) + '" start="' + start + '" stop="' + stop + '" channel="' + str(idChannel) + '" >' + "\n")
				f.write('<title>' + program['name'].encode('utf-8') + '</title>' + "\n")
				if 'description' in program.keys():
					f.write('<desc>' + program['description'].encode('utf-8') + '</desc>' + "\n")
				f.write('</programme>' + "\n")
				idProgram = idProgram + 1
			idChannel = idChannel + 1					
	f.write('</tv>' + "\n")
	f.close()


def m3uParse(file):	
	result = []
	f = fopen(file, 'r')
	for line in f.read().splitlines():
		if line.startswith('#EXTINF'):
			result.append(line.split(',')[1].lstrip().rstrip())
	f.close()
	return result
		
		
def wgetZip(url, file):
	import zlib
	response = requests.get(url)
	data = zlib.decompress(response.content, zlib.MAX_WBITS|32)
	with open(file, 'w') as f:
		f.write(data)
	

def getTagValue(f, tag, endtag, currentline):	
	line = currentline
	while '</' + endtag + '>' not in line:
		if '<' + tag in line:
			return line.split('<' + tag)[1].split('>')[1].split('<')[0]
		line = f.readline()	
	return ''
	

def xmltvParse(file):
	programs = {}
	channels = {}
	import codecs
	with codecs.open(file, "r", "utf-8") as f:
		line = f.readline()
		while line:
			if line.startswith('<channel'):
				id = line.split('id="')[1].split('"')[0]
				name = getTagValue(f, 'display-name', 'channel', line)
				programs[id] = []
				channels[name] = id			
			if line.startswith('<programme'):
				idChannel = line.split('channel="')[1].split('"')[0]
				ts = line.split('start="')[1].split('"')[0]					
				ts = datetime.datetime (
					year = int(ts[0:4]),
					month = int(ts[4:6]),
					day = int(ts[6:8]),
					hour = int(ts[8:10]),
					minute = int(ts[10:12]),
					tzinfo = timezone(int(ts[15:18]) * 3600)
				)
				name = getTagValue(f, 'title', 'programme', line)				
				desc = getTagValue(f, 'desc', 'programme', line)						
				programs[idChannel].append({'time': ts, 'name': name, 'description': desc})			
			line = f.readline()
	result = {}
	for channel in channels.keys():
		result[channel] = programs[channels[channel]]
	return result

	
def shiftTime(epg, deltaHours):
	result = {}
	for channel in epg.keys():
		programs = []
		for program in epg[channel]:
			program['time'] = program['time'] + datetime.timedelta(hours=deltaHours)
			programs.append(program)
		result.update({channel: programs})
	return result

def filterByName(epg, names):
	result = {}
	for channel in epg.keys():
		if channel in names:
			result.update({channel: epg[channel]})
	return result
	
def filterByDays(epg, days):
	today = datetime.date.today()
	tsstart = datetime.datetime (year = today.year, month = today.month, day = today.day, tzinfo = timezone(time.timezone))	
	tsend = tsstart + datetime.timedelta(days=days)	
	result = {}
	for channel in epg.keys():
		programs = []
		for program in epg[channel]:
			if program['time'] >= tsstart and program['time'] < tsend:
				programs.append(program)
		result.update({channel: programs})
	return result	
	
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

