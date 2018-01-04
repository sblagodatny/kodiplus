import os
import shutil
import hashlib


addon = 'plugin.program.epgscrapper'
version = '1.1'

basePath = os.getcwd()
addonSrcPath = basePath + '/src/' + addon
addonBuildPath = basePath + '/build/' + addon


def replaceInFile(file, strold, strnew):
	with open (file, 'r' ) as f:
		content = f.read()
	content = content.replace(strold, strnew)
	with open(file, "w") as f:
		f.write(content)
	
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
		
def removeFiles(path, extension):
	for file in os.listdir(path):
		if file.endswith('.' + extension):
			os.remove( os.path.join( path, file ) )
	
cversion = getCurrentVersion()
str = 'id="' + addon + '" version="' + cversion + '"'
strnew = str.replace(cversion, version)
replaceInFile(addonSrcPath + '/addon.xml', str, strnew)		
replaceInFile(basePath + '/addons.xml', str, strnew)
createMD5()
removeFiles(addonBuildPath,'zip')
buildFile = addonBuildPath + '/' + addon + '-' + version
shutil.make_archive(buildFile, 'zip', basePath + '/src/', addon)
