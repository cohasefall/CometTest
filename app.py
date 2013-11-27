from tornado import websocket, web, ioloop
import json
import threading
import serial
import signal
import os

clList = []
is_closing = False

# Read From SerialPort
def read_from_port(ser):
	while True:
		data = ser.readline().rstrip()
		if data != '':
			data = {"data": data}
			jsondata = json.dumps(data)

			for cl in clList:
				cl.write_message(jsondata)
		
# signal 
def signal_handler(signum, frame):
	global is_closing
	is_closing = True

def try_exit():
	global is_closing
	if is_closing:
		ioloop.IOLoop.instance().stop()

# Tornado 
class RootHandler(web.RequestHandler):
	def get(self):
		self.render("index.html")

class WebSocketHandler(websocket.WebSocketHandler):
	def open(self):
		if self not in clList:
			clList.append(self)
	
	def on_close(self):
		if self in clList:
			clList.remove(self)
			
class CometHandler(web.RequestHandler):
	@web.asynchronous
	def get(self, *args):
		#self.finish()
		data = {"message": "test"}
		data = json.dumps(data)
		self.write(data)
		self.finish()

 	@web.asynchronous
 	def post(self):
 		pass

settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "bower_components")
}

app = web.Application([
		(r'/', RootHandler),
		(r'/ws', WebSocketHandler),
		(r'/api', CometHandler),
		(r'/static/(.*)', web.StaticFileHandler, {'path': os.path.join(os.path.dirname(__file__), ".")})
])

if __name__ == '__main__':
	# Serial
	# ser = serial.Serial(4) # read from COM5
	# thread = threading.Thread(target=read_from_port, args=(ser,))
	# thread.setDaemon(True)
	# thread.start()
	
	# ctrl+c
	signal.signal(signal.SIGINT, signal_handler);
	
	app.listen(8080)
	ioloop.PeriodicCallback(try_exit, 100).start()
	ioloop.IOLoop.instance().start()

