#!/usr/bin/python
#
#
# simple web socket server... 
#
# https://github.com/opiate/SimpleWebSocketServer
# thanks @opiate
#
# @gitrc 2014
#

import signal, sys, ssl, logging
from SimpleWebSocketServer import WebSocket, SimpleWebSocketServer, SimpleSSLWebSocketServer
from optparse import OptionParser
from pprint import pprint

shared_secret = 'key007'

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)

class SimpleChat(WebSocket):

	def handleMessage(self):
		if self.data is None:
			self.data = ''
		payload = str(self.data)
		if payload.startswith(shared_secret):
			payload = payload.replace(shared_secret, '')
		
			for client in self.server.connections.itervalues():
				if client != self:
					try:
						client.sendMessage(payload)
					except Exception as n:
						print n

	#def handleConnected(self):
		#print self.address, 'connected'

	#def handleClose(self):
		#print self.address, 'closed'

if __name__ == "__main__":

	parser = OptionParser(usage="usage: %prog [options]", version="%prog 1.0")
	parser.add_option("--host", default='', type='string', action="store", dest="host", help="hostname (localhost)")
	parser.add_option("--port", default=8888, type='int', action="store", dest="port", help="port (8000)")
	parser.add_option("--ssl", default=0, type='int', action="store", dest="ssl", help="ssl (1: on, 0: off (default))")
	parser.add_option("--cert", default='./cert.pem', type='string', action="store", dest="cert", help="cert (./cert.pem)")
	parser.add_option("--ver", default=ssl.PROTOCOL_TLSv1, type=int, action="store", dest="ver", help="ssl version")
	
	(options, args) = parser.parse_args()

	cls = SimpleChat

	if options.ssl == 1:
		server = SimpleSSLWebSocketServer(options.host, options.port, cls, options.cert, options.cert, version=options.ver)
	else:	
		server = SimpleWebSocketServer(options.host, options.port, cls)

	def close_sig_handler(signal, frame):
		server.close()
		sys.exit()

	signal.signal(signal.SIGINT, close_sig_handler)

	server.serveforever()
