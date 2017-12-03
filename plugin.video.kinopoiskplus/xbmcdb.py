import xbmc
import os
from sqlite3 import dbapi2 as sqlite

dbPath = xbmc.translatePath("special://database")


def getDBFile(content):
	for f in os.listdir(dbPath):
		if content.lower() in f.lower():
			return f
	return None
	

def getVideoInfo(file, path):
	db = sqlite.connect(dbPath + '/' + getDBFile('videos'))
	try:
		result = db.execute("SELECT files.playCount, files.lastPlayed, streamdetails.iVideoDuration FROM files, path, streamdetails WHERE files.idPath = path.idPath AND files.idFile = streamdetails.idFile AND files.strFilename = ? AND path.strPath = ?",(file,path)).fetchone()
		info = {
			'playcount': result[0],
			'lastplayed': result[1],
			'duration': result[2]
		}
		db.close() 
		return info
	except:
		db.close()
		return None
