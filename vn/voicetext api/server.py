from tornado import web, ioloop
from tornado.log import enable_pretty_logging; enable_pretty_logging()
from subprocess import call
import json
import sys

class VoiceText(web.RequestHandler):

	def post(self):
		data = json.loads(self.request.body)
		call(['speak.bat', data.encode(sys.getfilesystemencoding())])

def get_app():
	return web.Application([
		(r'/voicetext', VoiceText),
	])

if __name__ == '__main__':
	app = get_app()
	app.listen(9871)
	main_loop = ioloop.IOLoop.instance()
	main_loop.start()
