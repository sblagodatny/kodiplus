# coding: utf-8


import xbmc
import xbmcgui
import kinopoisk
import os
from threading import Thread
import time
import util


class DialogSearch (xbmcgui.WindowXMLDialog):
	def select(self, control, title):
		result = xbmcgui.Dialog().select(title, self.values[control])
		if result!=-1:
			self.getControl(control).setLabel(self.values[control][result])		
	def input(self, control, title):	
		result = xbmcgui.Dialog().input(title, '', type=xbmcgui.INPUT_ALPHANUM)
		if result:
			self.getControl(control).setLabel(result)
	def setLabel(self, label, controls):
		for control in controls:
			self.getControl(control).setLabel(label)		
	def replaceAny(self, value):
		if value == self.any:
			return None
		return value
	def getFromDict(self, d, key):
		if key is None:
			return None
		return d[key]
	def onInit(self):
		self.action = None
		self.any = 'Любой'
		for control in [111,113,115,117]:
			self.getControl(control).setLabel(self.any)
		import datetime
		now = datetime.datetime.now()
		year = now.year
		self.periods = {}
		for d in [2,5,9]:
			self.periods[str(d)] = str(year - d) + ':'		
		self.values = {
			113: [self.any] + sorted(kinopoisk._genres.keys()),
			115: [self.any] + sorted(self.periods.keys()),
			117: [self.any] + sorted(kinopoisk._countries.keys())
		}
	def onClick(self, control):
		if control in [112,114,116]:
			self.select(control+1, self.getControl(control).getLabel())
			if self.getControl(control+1).getLabel() != self.any:
				self.setLabel(self.any,[111])
		if control == 110:
			self.input(control+1, self.getControl(control).getLabel())
			if self.getControl(control+1).getLabel() != self.any:
				self.setLabel(self.any,[113,115,117])
		if control == 118:
			self.action = 'movie'
			self.close()
		if control == 119:
			self.action = 'serial'
			self.close()	
	def result(self):
		if self.action is None:
			return None
		return {
			'action': self.action,
			'name': self.replaceAny(self.getControl(111).getLabel()),
			'genres': self.getFromDict(kinopoisk._genres, self.replaceAny(self.getControl(113).getLabel())),			
			'years': self.getFromDict(self.periods, self.replaceAny(self.getControl(115).getLabel())),
			'countries': self.getFromDict(kinopoisk._countries, self.replaceAny(self.getControl(117).getLabel())),
		}


class DialogDownloadStatus (xbmcgui.WindowXMLDialog):			

	def updater(self):		
		while self.updaterFlag:	
			torrent = self.data['function'](None, self.data['id'], self.data['hashString'])[0]['torrent']
			if torrent['percentDone'] == 1:
				break			
			eta = 'Unknown'
			if torrent['eta'] > 0:
				eta = time.strftime('%H:%M:%S', time.gmtime(torrent['eta']))
			completed = util.color('Completed: ','blue') + str(int(float(torrent['percentDone'])*100)) + '%' 
			completed = completed + '     ' + util.color('Remaining Time: ','blue') + eta
			self.getControl(110).setLabel(completed)
			details = util.color('Size: ','blue') + str(round((float(torrent["totalSize"]) / (1024*1024*1024)),2)) + 'Gb'
			details = details + '     ' + util.color('Seeds: ','blue') + str(torrent['peersSendingToUs'])
			details = details + '     ' + util.color('Rate: ','blue') + str(round((float(torrent["rateDownload"]) / (1024*1024)),2)) + 'Mbps'
			self.getControl(111).setLabel(details)			
			time.sleep(self.updaterDelay)
		self.close()	
			
	def stop(self):
		self.updaterFlag = False
		time.sleep(self.updaterDelay)	
	def setData(self, data):
		self.data = data
	def onInit(self):
		self.updaterFlag = True
		self.updaterDelay = 1		
		thread = Thread(target = self.updater)
		thread.start()
		
