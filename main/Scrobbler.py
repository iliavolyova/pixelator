import pylast
import time
from xml.dom.minidom import parseString

class Scrobbler(object):

	corrected_track = None
	firstrun = False

	def __init__(self, pix):
		self.pix = pix

		API_KEY = pix.config.creds['API_KEY']
		API_SECRET = pix.config.creds['API_SECRET']

		username = pix.config.creds['username']
		password_hash = pylast.md5(pix.config.creds['password'])


		self.network = pylast.get_lastfm_network(api_key = API_KEY,
												api_secret = API_SECRET,
												username = username,
												password_hash = password_hash)
		self.scrobbler = self.network.get_scrobbler('tst', '1.0')

	def callback_finished(self, sender, tracksearch, *callback_args):
		result = tracksearch.get_next_page()
		
		titlematch = str(result[0].get_title()).lower() != callback_args[1].lower()
		artistmatch = str(result[0].get_artist()).lower() != callback_args[0].lower()

		if not result or not result[0].get_album() or titlematch or artistmatch:
			self._title = callback_args[0]
			self._artist = callback_args[1]
			self._album = "-1-1-1ERROR"
			self._cover = '-1-1-1ERROR'
			self.pix.update_left([self._title, self._artist, self._album, self._cover])
			return (self._title, self._artist, self._album, self._cover)
		else:
			self.corrected_track = result[0]

		album = self.corrected_track.get_album()
		self._title = str(self.corrected_track.get_title())
		self._artist = str(self.corrected_track.get_artist())
		if not album.get_release_date() and len(album.get_release_date()) < 2:
			self._album = str(album.get_title())
		else: 
			self._album = str(album.get_title() + ' [' + album.get_release_date().split(' ')[2].replace(',', '.') + ']')
		
		self._cover = str(album.get_cover_image(size=pylast.COVER_LARGE))

		self.pix.update_left([self._title, self._artist, self._album, self._cover])

		self.time_started = int(time.time())
		self.firstrun = True
		return (self._title, self._artist, self._album, self._cover)

	def trackinfo(self, artist, title):			
		call_argsies = [artist, title]
		
		pylast.async_call(self, call=self.network.search_for_track, call_args=call_argsies,
			callback=self.callback_finished, callback_args=call_argsies)

	def do_now_playing(self):
		if self.firstrun:
			self.scrobbler.report_now_playing(self._artist, self._title)

	def do_scrobble(self):
		if self.firstrun:
			self.scrobbler.scrobble(artist = self._artist, 
								title = self._title, 
								time_started = self.time_started, 
								source = pylast.SCROBBLE_SOURCE_USER, 
								mode = pylast.SCROBBLE_MODE_PLAYED, 
								duration = 337)
	def parse(self, data):
		dom = parseString(data)
		xmlartist = dom.getElementsByTagName('artist')[0].toxml().replace('<artist>', '').replace('</artist>', '')
		xmltitle = dom.getElementsByTagName('title')[0].toxml().replace('<title>', '').replace('</title>', '')
		
		return (xmlartist, xmltitle)
