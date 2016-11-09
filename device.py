#! /usr/bin/env python

import os
import random
import time
import RPi.GPIO as GPIO
import alsaaudio
import wave
import random
from creds import *
import requests
import json
import re
import threading
from memcache import Client
import avs


class Device:

  def __init__(self):
    self.device = "plughw:1,0"
    self.audio = ''
    self.inp = None
    self.now_recording = False

  def recording(self):

    if self.inp is None:
	    self.inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL, self.device)
      self.inp.setchannels(1)
      self.inp.setrate(16000)
  		self.inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
  		self.inp.setperiodsize(500)
  		self.audio = ""
  		self.now_recording = True

    t = threading.Timer(5.0, lambda: self.now_recording = False)
    t.start()
    print("[STATE:RECORDING] started 5 seconds")
    while self.now_recording == True:
      l, data = self.inp.read()
      if l:
        self.audio += data
    t.cancel()
    print("[STATE:RECORDING] End")

    rf = open('recording.wav', 'w')
  	rf.write(audio)
  	rf.close()
  	inp = None

    print("[STATE:RECORDING] Send the voice")
    avs = Avs()
    avs.audio_palyer_callback = play
    avs.recognize()
    avs.close()

  def play(audio_stream):
    for d in audio_stream:
			if (len(d) >= 1024):
				audio = d.split('\r\n\r\n')[1].rstrip('--')
		with open("response.mp3", 'wb') as f:
			f.write(audio)
		os.system('mpg123 -q {}1sec.mp3 {}response.mp3'.format(path, path))
