import json
import util
import urllib
import os	
import base64	

# Transmission URL: http://127.0.0.1:9091/transmission/rpc
def send (session, url, data):
	headers = session.headers
	try:
		trSessId = session.cookies._find(name='SessionId', domain='transmission')
		tag = session.cookies._find(name='Tag', domain='transmission')
	except:
		trSessId = 'aaa'
		tag = 1			
	headers.update({'X-Transmission-Session-Id': trSessId})
	data.update({'tag': tag})
	
	reply = session.post(url, data = json.dumps(data), headers = headers)
	if not 'invalid session-id header' in reply.content:
		session.setCookie('transmission', 'Tag', tag + 1, True)		
		return (json.loads(reply.content))
	
	trSessId = reply.headers['X-Transmission-Session-Id']
	tag = 1
	headers.update({'X-Transmission-Session-Id': trSessId})
	data.update({'tag': tag})
	session.setCookie('transmission', 'SessionId', trSessId, True)
	session.setCookie('transmission', 'Tag', tag + 1, True)		
	
	reply = session.post(url, data = json.dumps(data), headers = headers)
	return (json.loads(reply.content))
	

def get (session, url, downloadsFolder=None):
	fields = ["id","name","percentDone","peersSendingToUs","rateDownload", "startDate","totalSize","eta","files","fileStats","hashString"]
	args = {"fields": fields}
	data = {
		"method": "torrent-get", 
		"arguments": args
	}
	reply = send(session,url,data)
	if reply["result"] != 'success':
		raise Exception ("Can't get torrents")
	result = []
	for torrent in reply["arguments"]["torrents"]:
		
		for i in range (0, len(torrent['files'])):
			torrent['files'][i]['id']=i
			torrent['files'][i].update(torrent['fileStats'][i])
		del torrent['fileStats']
		
		data = {'torrent': torrent}
		if downloadsFolder is not None:
			import xbmcvfs
			if xbmcvfs.exists(downloadsFolder + '/metadata/' + torrent['hashString']):
				data.update({'metadata': util.fileToObj(downloadsFolder + '/metadata/' + torrent['hashString'])})
		result.append(data)
	return result
	

def add (session, transmissionUrl, torrentUrl, downloadsFolder=None, metadata=None):
	file = os.path.dirname(os.path.realpath(__file__)) + '/' + 'temp.torrent'
	session.download(torrentUrl, file)
	f = open(file, "rb")
	encoded_string = base64.b64encode(f.read())		
	f.close()
	os.remove(file)
	data = {
		"method": "torrent-add", 
		"arguments": {"metainfo": encoded_string}
	}
	reply = send(session,transmissionUrl,data)
	if downloadsFolder is not None:
		import xbmcvfs
		if not xbmcvfs.exists(downloadsFolder + '/metadata/'):
			xbmcvfs.mkdir(downloadsFolder + '/metadata/')
		util.objToFile(metadata, downloadsFolder + '/metadata/' + reply["arguments"]["torrent-added"]["hashString"])
	return reply["arguments"]["torrent-added"]["id"]


def modify(session, url, hashString, data):
	args = {"ids": [hashString]}
	args.update(data)
	data = {
		"method": "torrent-set", 
		"arguments": args
	}
	reply = send(session,url,data)
	if reply["result"] != 'success':
		raise Exception ("Can't modify torrent")
	
	
def remove(session, url, hashString, deleteFiles=True, downloadsFolder=None):
	args = {"ids": [hashString], "delete-local-data": str(deleteFiles).lower()}
	data = {
		"method": "torrent-remove", 
		"arguments": args
	}
	reply = send(session,url,data)
	if reply["result"] != 'success':
		raise Exception ("Can't remove torrent")
	if downloadsFolder is not None:
		import xbmcvfs
		if xbmcvfs.exists(downloadsFolder + '/metadata/' + hashString):
			xbmcvfs.delete(downloadsFolder + '/metadata/' + hashString)

			
def update(hashString, downloadsFolder, metadata):
	util.objToFile(metadata, downloadsFolder + '/metadata/' + hashString)
