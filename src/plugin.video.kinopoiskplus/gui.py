# coding: utf-8


import xbmc
import xbmcgui
import kinopoisk
import os
from threading import Thread
import time
import util



class DialogDownloadStatus (xbmcgui.WindowXMLDialog):			

	def updater(self):
		self.getControl(100).setLabel(self.data['torrentName'])
		import transmission
		while self.updaterFlag:
			data = transmission.get(self.data['transmissionUrl'], [self.data['hashString']])[0]			
			if data['percentDone'] == 1:
				break
			eta = 'Unknown'
			if data['eta'] > 0:
				eta = time.strftime('%H:%M:%S', time.gmtime(data['eta']))
			completed = util.color('Completed: ','blue') + str(int(float(data['percentDone'])*100)) + '%' 
			completed = completed + '     ' + util.color('Remaining Time: ','blue') + eta
			self.getControl(110).setLabel(completed)
			details = util.color('Size: ','blue') + str(round((float(data["totalSize"]) / (1024*1024*1024)),2)) + 'Gb'
			details = details + '     ' + util.color('Seeds: ','blue') + str(data['peersSendingToUs'])
			details = details + '     ' + util.color('Rate: ','blue') + str(round((float(data["rateDownload"]) / (1024*1024)),2)) + 'Mbps'
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
		
