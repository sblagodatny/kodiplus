import time
import xbmc
import xbmcaddon
import SimpleHTTPServer
import BaseHTTPServer
import httplib
import traceback
import threading


_addon = xbmcaddon.Addon()
_path = _addon.getAddonInfo('path') + '/'
_port = int(_addon.getSetting('port'))

class MyHttpRequestHandler (SimpleHTTPServer.SimpleHTTPRequestHandler):
	def do_GET(self):
		
		try:
			import handlerKeshet
			url = handlerKeshet.resolve(None)
			self.send_response(302)
			self.send_header('Location',url)
		except:
			exc_type, exc_value, exc_traceback = sys.exc_info()
			log(traceback.format_exc(),xbmc.LOGERROR)		
			try:
				self.send_response(404)
			except:
				None
		try:
			self.end_headers()
		except:
			None

	def log_message(self, format, *args):
		return		
    

def log(message,loglevel=xbmc.LOGNOTICE):
	xbmc.log('service.urlresolver' + " : " + message,level=loglevel)


server = BaseHTTPServer.HTTPServer(('localhost', _port) , MyHttpRequestHandler)
thread = threading.Thread(target = server.serve_forever)
thread.deamon = True
thread.start()
log('Started on port ' + str(_port))
monitor = xbmc.Monitor()
monitor.waitForAbort(0)
server.shutdown()
log('Ended')
