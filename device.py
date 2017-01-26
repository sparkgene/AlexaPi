#! /usr/bin/env python

import os
import subprocess
import signal
import random
import time
import RPi.GPIO as GPIO
import alsaaudio
import wave
import random
from creds import *
import requests
import re
import threading
from memcache import Client
from avs import Avs
from Queue import Queue

audio_queue_lock = threading.Lock()

class Device:
    def __init__(self):
        self.__path = os.path.realpath(__file__).rstrip(os.path.basename(__file__))
        self.__avs = Avs(put_audio_to_device=(lambda x: self.enque(x)))
        # self.__avs = Avs(put_audio_to_device=(lambda x: self.play(x)))
        self.__avs.start()
        self.__audio_queue = Queue()
        self.__inp = None
        self.__device = "plughw:1,0"
        self.__recording = False
        self.__stop_device = False
        self.__audio_playing = False
        self.__check_audio_arrival_thread = threading.Thread(target=self.check_audio_arrival)
        self.__check_audio_arrival_thread.start()


    def active(self):
        return (self.__avs.active() or self.__recording)


    def is_idle(self):
        return self.__inp == None


    def wait_idle(self, seconds=0.5):
        while self.active() == True:
            time.sleep(seconds)


    def recording(self):
        audio = ''
        def stop_recording():
            self.__recording = False

        self.__init_device()

        t = threading.Timer(5.0, stop_recording)
        t.start()

        print("[STATE:DEVICE] recording started 5 seconds")
        self.__recording = True
        while self.__recording == True:
            l, data = self.__inp.read()
            if l:
                audio += data
        print("[STATE:DEVICE] recording End")
        self.__avs.put_audio(audio)


    def send_audio(self, audio):
        self.__avs.put_audio(audio)


    def check_audio_arrival(self):
        def play(audio):
            if audio is not None:
                print("[STATE:DEVICE] start play alexa response.")
                with open("response.mp3", 'w') as f:
                    f.write(audio)
                cmd = "mpg123 -q %s1sec.mp3 %sresponse.mp3" % (self.__path, self.__path)
                subprocess.call(cmd.strip().split(' '))
                print("[STATE:DEVICE] end play alexa response.")

        while True:
            if not self.__audio_queue.empty():
                print("[STATE:DEVICE] play alexa response.")
                with audio_queue_lock:
                    audio = self.__audio_queue.get()
                play(audio)

                if self.__avs.is_expect_speech():
                    self.recording()
                else:
                    self.__inp = None

            if self.__stop_device == True:
                break

            time.sleep(0.5)


    def enque(self, audio):
        print("[STATE:DEVICE] alexa response arrived.")
        with audio_queue_lock:
            self.__audio_queue.put(audio)


    def stop(self):
        self.__avs.close()
        self.__inp = None
        self.__check_audio_arrival_thread = None
        self.__stop_device = True


    def __init_device(self):
        if self.__inp is None:
          self.__inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL, self.__device)
          self.__inp.setchannels(1)
          self.__inp.setrate(16000)
          self.__inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
          self.__inp.setperiodsize(500)
          self.audio = ""
