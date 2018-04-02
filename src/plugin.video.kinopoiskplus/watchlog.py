from sqlite3 import dbapi2 as sqlite



def init(path, pathInit):
	import os
	if not os.path.isfile(path + 'watchlog.db'):
		import shutil
		shutil.copyfile(pathInit + 'watchlog.db', path + 'watchlog.db')			
			
			
def isWatched(path, addon, item):
	db = sqlite.connect(path + 'watchlog.db')
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
		
def setWatched(path, addon, item):
	if isWatched(path, addon, item):
		return
	db = sqlite.connect(path + 'watchlog.db')
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
		
def setUnWatched(path, addon, item):
	db = sqlite.connect(path + 'watchlog.db')
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

