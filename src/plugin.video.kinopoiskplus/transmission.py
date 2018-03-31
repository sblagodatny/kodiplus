import json
import util
import urllib
import os	
import base64	
import xbmcvfs
import requests

# Transmission URL: http://127.0.0.1:9091/transmission/rpc
def send (url, data):
	session = requests.Session()
	reply = session.post(url)
	sid = reply.headers['X-Transmission-Session-Id']
	session.headers.update({'X-Transmission-Session-Id': sid})
	data['tag'] = 1
	reply = session.post(url, data = json.dumps(data))
	return (json.loads(reply.content))
	
	
	

def get (url, hashList=None):
	fields = ["id","name","percentDone","peersSendingToUs","rateDownload", "startDate","totalSize","eta","files","fileStats","hashString"]
	args = {"fields": fields}
	if hashList is not None:
		args["ids"]=hashList
	data = {
		"method": "torrent-get", 
		"arguments": args
	}
	reply = send(url,data)
	if reply["result"] != 'success':
		raise Exception ("Can't get torrents")
	result = []
	for torrent in reply["arguments"]["torrents"]:
		for i in range (0, len(torrent['files'])):
			torrent['files'][i]['id']=i
			torrent['files'][i].update(torrent['fileStats'][i])
		del torrent['fileStats']
		result.append(torrent)
	return result
	

def add (url, torrentUrl, pathCookies):
	session = requests.Session()
	session.verify = False
	util.loadCookies(session, pathCookies)
	util.setUserAgent(session, 'chrome')
	file = os.path.dirname(os.path.realpath(__file__)) + '/' + 'temp.torrent'	
	import xbmcvfs
	output = xbmcvfs.File (file, 'w')
	r = session.get(torrentUrl)
	for chunk in r.iter_content(chunk_size=1024): 
		if chunk:
			output.write(chunk)
	output.close()
	f = open(file, "rb")
	encoded_string = base64.b64encode(f.read())		
	f.close()
	os.remove(file)
	data = {
		"method": "torrent-add", 
		"arguments": {"metainfo": encoded_string}
	}
	reply = send(url,data)
	return reply["arguments"]["torrent-added"]["hashString"]
	


def modify(url, hashString, data):
	args = {"ids": [hashString]}
	args.update(data)
	data = {
		"method": "torrent-set", 
		"arguments": args
	}
	reply = send(url,data)
	if reply["result"] != 'success':
		raise Exception ("Can't modify torrent")
	
	
def remove(url, hashString, deleteFiles=True):
	args = {"ids": [hashString], "delete-local-data": str(deleteFiles).lower()}
	data = {
		"method": "torrent-remove", 
		"arguments": args
	}
	reply = send(url,data)
	if reply["result"] != 'success':
		raise Exception ("Can't remove torrent")

