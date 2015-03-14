import os
from random import shuffle

class FileManager(object):

	def __init__(self, gifdir):
		self.gifdir = gifdir
		self.giflist = []
		self.giflist = self.gif_list(gifdir)
		shuffle(self.giflist)
		self.gifcounter = 0

	def gif_list(self, mydir):
		for (dirpath, dirnames, filenames) in os.walk(mydir):
			self.giflist.extend(os.path.join(dirpath, myfile) for myfile in filenames)
			for dirname in dirnames:
				self.gif_list(os.path.join(dirpath,dirname))
			break

		return self.giflist

	def next_gif(self):
		gif_path = self.giflist[self.gifcounter % len(self.giflist)]
		self.gifcounter += 1
		return gif_path

if __name__ == '__main__':
	f = FileManager("../../gif")
	print f.gif_list(f.gifdir)
