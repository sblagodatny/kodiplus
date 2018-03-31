import cPickle as pickle
from sqlite3 import dbapi2 as sqlite

def init(path, pathInit):
	import os
	if not os.path.isfile(path + 'cache.db'):
		import shutil
		shutil.copyfile(pathInit + 'cache.db', path + 'cache.db')

			
def get(id, path):
	db = sqlite.connect(path + 'cache.db')
	result = db.execute("SELECT object FROM cache WHERE id=?",(id,)).fetchone()
	if result is None:
		db.close()
		return None
	db.execute("UPDATE cache SET accessed = datetime('now', 'localtime') WHERE id = ?",(id,))						
	db.commit()
	db.close()
	return (pickle.loads(str(result[0])))
		

def set(id, obj, path):
	db = sqlite.connect(path + 'cache.db')
	result = db.execute("SELECT rowid FROM cache WHERE id = ?",(id,)).fetchone()
	bobj = sqlite.Binary(pickle.dumps(obj))
	if result is None:
		db.execute("INSERT INTO cache (id, object, created, modified, accessed) VALUES (?,?,datetime('now', 'localtime'),datetime('now', 'localtime'),datetime('now', 'localtime'))",(id, bobj))
	else:
		db.execute("UPDATE cache SET accessed = datetime('now', 'localtime'), modified = datetime('now', 'localtime'), object = ? WHERE id = ?",(id, bobj))
	db.commit()
	db.close()
