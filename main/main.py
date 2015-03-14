import kivy
kivy.require('1.8.0')

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ObjectProperty, ListProperty
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.config import Config

from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from functools import partial
from random import randint
from FileManager import FileManager
from Scrobbler import Scrobbler	
from magnet import Magnet 

import socket
import urllib2

class Pixelator(BoxLayout):

	label_title = ObjectProperty(text="")
	label_artist = ObjectProperty(text="")
	label_album = ObjectProperty(text="")
	labels = ListProperty([])

	master_pane = ObjectProperty()
	left_pane = ObjectProperty()
	magnet_box = ObjectProperty()

	img_left = ObjectProperty() 
	img_right = ObjectProperty()
	fmanager = None

	current_song = None

	timeout = 10

	def __init__(self, **kwargs):
		super(BoxLayout, self).__init__(**kwargs)
		self.fmanager = FileManager("../../gif")
		self.scrobbler = Scrobbler(self)
		
		self.img_right.source = self.fmanager.next_gif()
		self.labels.extend([self.label_title, self.label_artist, self.label_album])

		self.label_title.text = "[size=35]Play me[/size]"
		self.label_artist.text = "[size=35]Some[/size]"
		self.label_album.text = "[size=35]Riffs[/size]"
		socket.setdefaulttimeout(self.timeout)

	def update_right(self, dt):
		self.animate_right()

	def async_trackinfo(self, artist, title):
		self.scrobbler.trackinfo(artist, title)

	def update_left(self, track):
		for i in range(0,3):
			Clock.schedule_once(partial(self.animate_labels, i, track), i/10.)
		self.animate_cover(track[3])

	def animate_cover(self, url):
		fade = Animation(color=[0,0,0,0], d=3, t='out_circ')
		fade.bind(on_complete=partial(self.change_cover, url))
		grow = Animation(color=[1,1,1,1], d=3, t='in_circ')
		if url != "-1-1-1ERROR":
			animation = fade + grow
		else:
			animation = fade
		animation.start(self.img_left)

	def change_cover(self, url, *largs):
		self.img_left.source = url

	def animate_labels(self, i, lbl_data, *largs):
		posx = self.labels[i].pos[0]
		left = Animation(x=posx - self.labels[i].width - 50, t='in_circ', d=3)
		left.bind(on_complete=partial(self.update_text, i, lbl_data))
		right = Animation(x=posx, t='out_circ', d=3)
		animation = left + right
		animation.start(self.labels[i])

	def update_text(self, i, lbl_data, *largs):
		fontsize = (65 if len(lbl_data[i]) < 20 else 45)
		base_string = '[size=40]%s[/size] [size=%d]%s[/size]'
		base_text = ["Title: ", "Artist: ", "Album: "]
		if lbl_data[i] != "-1-1-1ERROR":
			self.labels[i].text = base_string % (base_text[i], fontsize, lbl_data[i])
		else:
			self.labels[i].text = ''	

	def animate_right(self):
		down = Animation(y=self.img_right.pos[1] - Window.height, t='in_circ')
		down.bind(on_complete=self.change_right_pic)
		up = Animation(center_y = Window.height / 2, t='out_circ')
		animation = down + up
		animation.start(self.img_right)

	def change_right_pic(self, instance, value):
		self.img_right.source = self.fmanager.next_gif()

	def check_song_server(self, dt):
		req = urllib2.Request('http://192.168.1.35:8080')
		site = urllib2.urlopen(req)
		s = site.readlines()
		if s:
			artist, title = self.scrobbler.parse(s[1])
			if title != self.current_song:
				self.scrobbler.do_scrobble()
				self.current_song = title
				self.async_trackinfo(artist, title)
	
	def update_now_playing(self, dt):
		if self.current_song:
			self.scrobbler.do_now_playing()

class PixelatorApp(App):

	def build(self):
		Config.set('graphics', 'width', '1920')
		Config.set('graphics', 'height', '1056')
		Config.write()

		pix = Pixelator()
		Clock.schedule_interval(pix.update_right, 20)
		Clock.schedule_interval(pix.check_song_server, 2) 
		#Clock.schedule_interval(pix.update_now_playing, 1)
		return pix

if __name__ == '__main__':
	PixelatorApp().run()
