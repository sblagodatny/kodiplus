import os
import shutil
import hashlib


addon = 'plugin.video.kinopoiskplus'
version = '1.2'

basePath = os.getcwd()
addonSrcPath = basePath + '/src/' + addon
addonBuildPath = basePath + '/build/' + addon


def replaceInFile(file, strold, strnew):
	tmp = basePath + '/tmp'
	with open(file, "rt") as fin:
		with open(tmp, "wt") as fout:
			for line in fin:
				fout.write(line.replace(strold, strnew))
	os.remove(file)
	shutil.copy(tmp, file)
	os.remove(tmp)
	
def getCurrentVersion():
	with open (addonSrcPath + '/addon.xml', 'r' ) as f:
		content = f.read()
	return (content.split('id="' + addon + '" version="')[1].split('"')[0])
	
def createMD5():
	with open (basePath + '/addons.xml', 'r' ) as f:
		content = f.read()
	md5 = hashlib.md5(content).hexdigest()
	with open(basePath + '/addons.xml.md5', "w") as f:
		f.write(md5)
		
	
cversion = getCurrentVersion()
str = 'id="' + addon + '" version="' + cversion + '"'
strnew = str.replace(cversion, version)
replaceInFile(addonSrcPath + '/addon.xml', str, strnew)		
replaceInFile(basePath + '/addons.xml', str, strnew)
createMD5()
shutil.make_archive(addonBuildPath + '/' + addon + '-' + version + '.zip', 'zip', addonSrcPath)
