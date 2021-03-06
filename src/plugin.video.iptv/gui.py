# coding: utf-8


import pyxbmct
import xbmcgui
import util
import xbmc
import streams

from datetime import datetime
from pytz import timezone


class DialogEPG(pyxbmct.AddonDialogWindow):

	def __init__(self, playlistFile, epgFile, iconsFolder, timezone):
		super(DialogEPG, self).__init__('IPTV')
		self.setGeometry(1150, 600, 3, 3)
		
		self.timezone = timezone
		self.channels = util.m3uChannels(playlistFile)
		self.epg = util.xmltvParse(epgFile,self.timezone)
		self.connect(pyxbmct.ACTION_NAV_BACK, self.close)
		self.connect(pyxbmct.ACTION_PREVIOUS_MENU, self.close)
		self.connectEventList([ 
			pyxbmct.ACTION_MOVE_DOWN,
			pyxbmct.ACTION_MOVE_UP,
			pyxbmct.ACTION_MOUSE_WHEEL_DOWN,
			pyxbmct.ACTION_MOUSE_WHEEL_UP,
			pyxbmct.ACTION_MOUSE_MOVE],
            self.handleEvent)
		
		
		### Setup channels list ###
		self.listChannels = pyxbmct.List(_imageWidth=20, _imageHeight=20 )
		self.placeControl(self.listChannels, 0,0, rowspan=2, columnspan=1)  
		for channel in self.channels:
			item = xbmcgui.ListItem(channel['name'], iconImage=iconsFolder + channel['tvg_logo'])									
			self.listChannels.addItem(item)
		self.connect(self.listChannels, lambda: self.play())					
		
		### Setup programs list ###
		self.listPrograms = pyxbmct.List()
		self.placeControl(self.listPrograms, 0,1, rowspan=2, columnspan=2)  		
		
		### Setup description textbox ###
		self.textboxDescription = pyxbmct.TextBox()
		self.placeControl(self.textboxDescription, 2, 0, rowspan=1, columnspan=3)
		self.textboxDescription.autoScroll(1000, 1000, 1000)

		### Setup navigation ###
		self.listChannels.setNavigation(self.listPrograms, self.listPrograms, self.listPrograms, self.listPrograms)
		self.listPrograms.setNavigation(self.listChannels, self.listChannels, self.listChannels, self.listChannels)
		self.setFocus(self.listChannels)
		self.selectedChannel=None
		self.selectedProgram=None
		self.selectChannel()	
		
				
	def handleEvent(self):
		if self.getFocus() == self.listChannels:
			self.selectChannel()
		if self.getFocus() == self.listPrograms:
			self.selectProgram()
			
	def select(self, item):
		item.setLabel(util.color(util.bold(item.getLabel()),'orange'))
	
	def unselect(self, item):
		item.setLabel(util.uncolor(util.unbold(item.getLabel()),'orange'))
		
	def selectChannel(self):		
		if self.selectedChannel is not None:
			self.unselect(self.listChannels.getListItem(self.selectedChannel))
		self.selectedChannel = self.listChannels.getSelectedPosition()
		self.select(self.listChannels.getListItem(self.selectedChannel))
		self.listPrograms.reset()
		self.textboxDescription.setText(' ')
		if 'tvg_id' not in self.channels[self.selectedChannel].keys():
			return		
		tvg_id = self.channels[self.selectedChannel]['tvg_id']	
		if tvg_id not in self.epg.keys():
			return
		now = datetime.now(timezone(self.timezone))
		self.deletedPrograms = 0
		for program in self.epg[tvg_id]:
			if now < program['stop']:
				self.listPrograms.addItem(program['start'].strftime("%H:%M") + '  ' + program['title'])
			else:
				self.deletedPrograms = self.deletedPrograms + 1
		self.selectedProgram=None
		self.selectProgram()	
		
		
	def selectProgram(self):
		if self.selectedProgram is not None:
			self.unselect(self.listPrograms.getListItem(self.selectedProgram))
			self.selectedProgram = self.listPrograms.getSelectedPosition()
		else:
			self.selectedProgram=0
		self.select(self.listPrograms.getListItem(self.selectedProgram))
		tvg_id = self.channels[self.selectedChannel]['tvg_id']
		program = self.epg[tvg_id][self.selectedProgram + self.deletedPrograms]
		self.textboxDescription.setText(program['description'])
		
	
	def play(self):
		channel = self.channels[self.selectedChannel]
		url = channel['url']
		headers = None
		if channel['name'] == 'קשת':
			url, headers = streams.getKeshetStream()
		if channel['name'] == 'רשת':
			url, headers = streams.getReshetStream()
		util.play(url,channel['name'],headers)
	
		
		