from sqlite3 import dbapi2 as sqlite


def init(dbfile,initfile):
	import os
	if not os.path.isfile(dbfile):
			import shutil
			shutil.copyfile(initfile, dbfile)

			
def isWatched(dbfile, addon, item):
	db = sqlite.connect(dbfile)
	try:
		result = db.execute("SELECT item FROM watchlog WHERE addon = ? AND item = ?",(addon,unicode(item))).fetchone()		
		db.close() 
		if result is None:
			return False
		else:
			return True
	except:
		try:
			db.close()
		except:
			None
		raise
		
def setWatched(dbfile, addon, item):
	if isWatched(dbfile, addon, item):
		return
	db = sqlite.connect(dbfile)
	try:
		result = db.execute("INSERT INTO watchlog (addon,item) VALUES (?,?)",(addon,unicode(item)))		
		db.commit()
		db.close() 
	except:
		try:
			db.close()
		except:
			None
		raise
		
def setUnWatched(dbfile, addon, item):
	db = sqlite.connect(dbfile)
	try:
		result = db.execute("DELETE FROM watchlog WHERE addon = ? AND item = ?",(addon,unicode(item)))		
		db.commit()
		db.close() 
	except:
		try:
			db.close()
		except:
			None
		raise

