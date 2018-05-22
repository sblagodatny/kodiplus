import sys
import cPickle as pickle
import requests
import time
import datetime
import xbmcvfs
from bs4 import BeautifulSoup
import xbmcgui
import xbmc
import os
import HTMLParser	
from pytz import timezone
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

_htmlEscape = {
	"&amp;": "&",
	"&lt;": "<",
	"&gt;": ">",
	"&#39;": "'",
	"&quot;": '"',
	"\/": '/',
	"&thinsp;": ' ',
	"&ndash;": '-'
}
		
def unescape(str):
	return(HTMLParser.HTMLParser().unescape(nvl(str,'')))
		
def unsecapelist(list):
	result = []
	for l in list:
		result.append(unescape(l))

	
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
	
def uncolor(str, color):
	return str.replace('[COLOR ' + color + ']','').replace('[/COLOR]','')
	
def bold(str):
	return '[B]' + str + '[/B]'
	
def unbold(str):
	return str.replace('[B]','').replace('[/B]','')
	
	
	
### File utilities ###	
def objToFile(obj, path):
	with open(path, 'wb') as output:
		pickle.dump(obj, output, protocol=pickle.HIGHEST_PROTOCOL)
	
def fileToObj(path):
	with open(path, 'rb') as input:
		obj = pickle.load(input)
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

	
### Requests Utilities ###	

def setUserAgent(session, agent):
	agents = {
		'chrome': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
		'firefox': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'
	}
	session.headers['User-Agent'] = agents[agent]

def saveCookies(session, path):
	objToFile(session.cookies, path)
	
def loadCookies(session, path):
	if os.path.isfile(path):
		session.cookies = fileToObj(path)

def setCookie(session, domain, name, value):
	args = {
		'domain': domain,
		'expires': None,
		'path': '/',
		'version':0
	}
	session.cookies.set(name=name, value=value, **args)

def headerCookie(cookiesdict):
	headers = {'Cookie': "; ".join([str(x)+"="+str(y) for x,y in cookiesdict.items()])}	
	return headers
	

	
### Date Utilities ###
def parseDateTimeUTC(str):
	t = datetime.datetime.fromtimestamp(time.mktime(time.strptime(str[0:14], "%Y%m%d%H%M%S")))
	offset = int(str[15:18])
	t = t - datetime.timedelta(hours=offset)
	return t
	
	
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
	
	
def xmltvParse(epgFile,localtz):
	tz=timezone(localtz)
	epg = {}
	f = xbmcvfs.File (epgFile, 'r')
	data = f.read()
	f.close()
	data = BeautifulSoup(data, "html.parser")
	for program in data.find_all('programme'):
		start = tz.fromutc(parseDateTimeUTC(program['start']))
		stop = tz.fromutc(parseDateTimeUTC(program['stop']))
		if program['channel'] not in epg.keys():
			epg.update({program['channel']:[]})
		epg[program['channel']].append({
			'title': program.find('title').get_text(), 
			'description': program.find('desc').get_text(),
			'start': start,
			'stop':stop 
		})
	return epg

		
		
### External Player ###
def play(url, title, headers=None, forceKodiPlayer=False):
	if forceKodiPlayer:
		item = xbmcgui.ListItem(title)
		murl = url
		if headers is not None:
			murl = murl + '|'
			for header, value in headers.iteritems():
				murl = murl + header + '=' + value + '&'
		xbmc.Player().play(murl, item)
		return
	if xbmc.getCondVisibility('system.platform.android'):
		cmd=[
			'am','start','-n','com.mxtech.videoplayer.ad/.ActivityScreen','-d',url,'--user','0','--activity-clear-task',
			'--es','title',unicode(title)
		]
		if headers is not None:
			headersS = ''
			empty = True
			for key, value in headers.iteritems():
				headersS = headersS + key + ',' + value + ','
				empty = False
			if not empty:
				headersS = headersS[:-1]
				cmd = cmd + ['--esa', 'headers', headersS]
	elif xbmc.getCondVisibility("system.platform.windows"):
		cmd=[
			'C:/Program Files/VideoLAN/VLC/vlc.exe','--meta-title=' + unicode(title), url
		]
	else:
		xbmcgui.Dialog().ok('Error', 'Unsupported OS')
		return
	import subprocess
	p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout, stderr = p.communicate()
#	xbmcgui.Dialog().ok('Player', stdout, stderr)
