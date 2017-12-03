import datetime
import util

def init(path):
	c = util.fileToObj(path + '/cache')
	if c is None:
		return {}
	return c
	
def flush(c, path):
	util.objToFile(c, path + '/cache')
	
def get(c, id):
	if id in c.keys():
		c[id]['ts'] = datetime.datetime.today()
		return c[id]['obj']
	return None

def set(c, id, obj):
	c[id] = {'obj': obj, 'ts': datetime.datetime.today()}

def remove(c, id):
	del c[id]

def purge(c, age):
	now = datetime.datetime.today()
	for id in c.keys():
		cage = now - c[id]['ts']
		if cage.days > age:
			del c[id]

