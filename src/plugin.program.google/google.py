from bs4 import BeautifulSoup
import requests
import util
import os
import time
import copy
import json



def initSession(pathCookies=None):
	session = requests.Session()
	session.verify = False
	util.setUserAgent(session, 'chrome')
	return session

	
def login (pathCookies, email, password):

	session=initSession()		
	
	######## Step 1 #########
	content = session.get('https://accounts.google.com/Login').text
	dummy, i = util.substr ('window.WIZ_global_data','= ',content)
	data = json.loads(util.parseBrackets(content, i, ['{','}']))
	data = data['OewCAd']
	p1 = data = data.split(',')[3].replace('"','').replace(']','')
	soap = BeautifulSoup(content, "html.parser")
	data = soap.find("div", {"id" : "view_container"})['data-initial-setup-data'].replace('%.@.','[')
	data = json.loads(data)
	data = data[13] 
	p2 = json.dumps(data).replace('"','')
	
	######## Step 2 #########
	session.headers.update ({
		'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
		'Google-Accounts-XSRF': '1',
		'Referer': 'https://accounts.google.com/',
		'X-Same-Domain': '1'
	})			
	data = {
#		'continue': 'https://myaccount.google.com/',
		'continue': 'https://accounts.google.com/ManageAccount',
		'f.req': '["' + email + '","' + p2 + '",[],null,"IL",null,null,2,false,true,[null,null,[2,1,null,1,"https://accounts.google.com/ServiceLogin?requestPath=%2FLogin&Page=PasswordSeparationSignIn",null,[],4],1,[null,null,[]],null,null,null,true],"' + email + '"]',
		'azt': p1,
		'deviceinfo': '[null,null,null,[],null,"IL",null,null,[],"GlifWebSignIn",null,[null,null,[]]]',
		'gmscoreversion': 'undefined',
		'checkConnection': 'youtube:841:0',
		'checkedDomains': 'youtube',
		'pstMsg': '1'
	}
	content = session.post('https://accounts.google.com/_/signin/sl/lookup?hl=en&_reqid=73079&rt=j', data=data).text
	data = json.loads(content.replace(")]}'","").replace("\n",""))
	data = data[0][0][2]
	p3 = json.dumps(data).replace('"','')
	
	
	######## Step 3 #########
	data = {
		'continue': 'https://accounts.google.com/ManageAccount',
#		'continue': 'https://myaccount.google.com/',
		'f.req': '["' + p3 + '",null,1,null,[1,null,null,null,["' + password + '",null,true]],[null,null,[2,1,null,1,"https://accounts.google.com/ServiceLogin?requestPath=%2FLogin&Page=PasswordSeparationSignIn",null,[],4],1,[null,null,[]],null,null,null,true]]',
		'azt': p1,
		'deviceinfo': '[null,null,null,[],null,"IL",null,null,[],"GlifWebSignIn",null,[null,null,[]]]',
		'gmscoreversion': 'undefined',
		'checkConnection': 'youtube:841:0',
		'checkedDomains': 'youtube',
		'pstMsg': '1'
	}	
	content = session.post('https://accounts.google.com/_/signin/sl/challenge?hl=en&_reqid=173079&rt=j', data=data).text
	if 'SID' not in str(session.cookies):
		raise Exception('Unable to login: Invalid credentials')	
	
	######## Step 4 #########
	util.resetHeaders(session)
	content = session.get( 'https://studio.youtube.com').text
#	dummy, i = util.substr ("yt.setConfig('GOOGLE_HELP_PRODUCT_DATA'",', ',content)
#	data = json.loads(util.parseBrackets(content, i, ['{','}']))
#	channel = data['channel_external_id']
#	soap = BeautifulSoup(content, "html.parser")
#	name = soap.find("div", class_='yt-masthead-picker-name').get_text()
	channel = 'UCjz_C9FQC6uAg1G-boqqW0g'
	name = 'Stas Blagodatny'
	
	### Save login data ###	
	loginInfo = email + '&' + channel + '&' + name + '&' + str(time.time())	
	util.setCookie(session, 'www.google.com', 'MyLoginInfo', loginInfo)
	util.saveCookies(session, pathCookies)	

	
def getLoginInfo(session):	
	try:
		loginInfo = session.cookies._find(name='MyLoginInfo', domain='www.google.com').split('&')
		return ({
			'email': loginInfo[0],			
			'channel': loginInfo[1],
			'name': loginInfo[2],
			'ts': float(loginInfo[3])
		})
	except:
		return None

