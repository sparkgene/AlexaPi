#! /usr/bin/env python

import os
import signal
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
from avs import Avs


class Device:

  def __init__(self):
    self.device = "plughw:1,0"
    self.audio = ''
    self.inp = None
    self.now_recording = False
    self.path = os.path.realpath(__file__).rstrip(os.path.basename(__file__))
    self.avs = Avs(self.recording, (lambda x: self.play(x)))
    self.avs.start()
    self.expect_speech = True

  def recording(self):
    def stop_recording():
      self.now_recording = False

    self.expect_speech = False
 
    if self.inp is None:
      self.inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL, self.device)
      self.inp.setchannels(1)
      self.inp.setrate(16000)
      self.inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
      self.inp.setperiodsize(500)
      self.audio = ""
      self.now_recording = True

    t = threading.Timer(5.0, stop_recording)
    t.start()
    self.audio = ''
    self.now_recording = True
    print("[STATE:RECORDING] started 5 seconds")
    while self.now_recording == True:
      l, data = self.inp.read()
      if l:
        self.audio += data
    t.cancel()
    print("[STATE:RECORDING] End")

    self.avs.put_audio(self.audio)

  def play(self, audio_stream):
    if audio_stream is not None:    
      with open("response.mp3", 'w') as f:
        f.write(audio_stream)
      os.system('mpg123 -q {}1sec.mp3 {}response.mp3'.format(self.path, self.path))
    
    self.expect_speech = True
    self.inp = None

  def stop(self):
    self.avs.close()
    self.inp = None
