import requests

import time

import json
import os

import matplotlib
from matplotlib.pyplot import figure
import matplotlib.pyplot as plt
import matplotlib.animation as animation

import numpy as np
import wave

import pygame
import threading

pygame.mixer.init()

# TODO
def acquire_token():
	os.system("chrome https://developer.spotify.com/console/get-audio-analysis-track/")


oauth_token = "<Token>"
track_id = "0wydxbEaB3KSKJstJVhTG5"

headers = {
	'Authorization': 'Bearer ' + oauth_token,
}

response = requests.get('https://api.spotify.com/v1/audio-analysis/' + track_id, headers=headers)
json_response = response.json()

if response.status_code != 200:
	print("Error: status_code")
	print(response.text)
	acquire_token()
	exit()

if json_response["meta"]["status_code"] != 0:
	print("Error: meta status_code")
	print(json_response)
	acquire_token()
	exit()

print("Info for " + requests.get("https://api.spotify.com/v1/tracks/" + track_id, headers=headers).json()["name"])

current_pos = 0
line = None

class AudioAnalysis:
	def __init__(self, bars, beats, sections, segments, tatums):
		self.bars = bars
		self.beats = beats
		self.sections = sections
		self.segments = segments
		self.tatums = tatums

	def __str__(self):
		return f"<AudioAnalysis bars: {len(self.bars)}, beats: {len(self.beats)}, sections: {len(self.sections)}, segments: {len(self.segments)}, tatums: {len(self.tatums)}>"

	def __repr__(self):
		return str(self)

	def plot(self):
		global line
		pygame.mixer.init()

		fig = figure(figsize=(30, 15))
		ax = fig.add_subplot(111)

		# bars
		xs = [itm.start for itm in self.bars]
		ys = [0.0002 for itm in self.bars]
		ss = [itm.duration for itm in self.bars]
		ax.scatter(xs, ys, s=ss)

		# beats
		xs = [itm.start for itm in self.beats]
		ys = [0.0001 for itm in self.beats]
		ss = [itm.duration for itm in self.beats]
		ax.scatter(xs, ys, s=ss)

		# sections
		[ax.plot([section.start, section.start+section.duration], [0.0003, 0.0003]) for section in self.sections]

		# segments
		[ax.plot([segment.start, segment.start+segment.duration], [0.0004, 0.0004]) for segment in self.segments]

		# tatums
		xs = [itm.start for itm in self.tatums]
		ys = [0 for itm in self.tatums]
		ss = [itm.duration for itm in self.tatums]
		ax.scatter(xs, ys, s=ss)

		# audio
		spf = wave.open('crypteque.wav','r')
		signal = spf.readframes(-1)
		signal = np.fromstring(signal, 'Int16')
		fs = spf.getframerate()
		spf.close()

		line, = ax.plot([0, 0], [-0.0001, 0.0005], 'k-')
		def audio():
			global current_pos
			print("Playing")
			pygame.mixer.music.load('crypteque.wav')
			pygame.mixer.music.play(0)
		
		audio_thread = threading.Thread(target=audio, args=())
		audio_thread.start()

		def animate(i):
			global current_pos, line
			current_pos = pygame.mixer.music.get_pos()
			line.remove()
			line, = ax.plot([current_pos/1000, current_pos/1000], [-0.0001, 0.0005], 'k-')

		ani = animation.FuncAnimation(fig, animate, interval=1)
		plt.show()


class TimeInterval:
	def __init__(self, start, duration, confidence):
		self.start = start
		self.duration = duration
		self.confidence = confidence

class Section:
	def __init__(self, args):
		self.args = args
		self.start = args["start"]
		self.duration = args["duration"]

	def __str__(self):
		return f"<Section {self.args}>"

	def __repr__(self):
		return str(self)

class Segment:
	def __init__(self, args):
		self.args = args
		self.start = args["start"]
		self.duration = args["duration"]

	def __str__(self):
		return f"<Segment {self.args}>"

	def __repr__(self):
		return str(self)
# bars
bars = []
for interval in json_response["bars"]:
	bars.append(TimeInterval(interval["start"], interval["duration"], interval["confidence"]))

# beats
beats = []
for interval in json_response["beats"]:
	beats.append(TimeInterval(interval["start"], interval["duration"], interval["confidence"]))

sections = []
for section in json_response["sections"]:
	sections.append(Section(section))

segments = []
for segment in json_response["segments"]:
	segments.append(Segment(segment))

tatums = []
for interval in json_response["tatums"]:
	tatums.append(TimeInterval(interval["start"], interval["duration"], interval["confidence"]))

analysis = AudioAnalysis(bars, beats, sections, segments, tatums)

print(analysis)
analysis.plot()