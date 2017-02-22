#! /usr/bin/env python

import os
import subprocess
import signal
import random
import time
import RPi.GPIO as GPIO
# import alsaaudio
import wave
from creds import *
import requests
import re
import threading
# from memcache import Client
from avs import Avs
from Queue import Queue
from device_state import DeviceState

audio_queue_lock = threading.Lock()

class Device:
    def __init__(self, recorder=None):
        self.__path = os.path.realpath(__file__).rstrip(os.path.basename(__file__))
        # self.__avs = Avs(put_audio_to_device=(lambda x: self.enque(x)))
        self.__avs = Avs(put_audio_to_device=(lambda x: self.play(x)))
        self.__avs.start()
        self.recorder = recorder
        self.__audio_queue = Queue()
        self.__device_state = DeviceState()
        self.__inp = None
        self.__device = "plughw:1,0"
        self.__recording = False
        self.__stop_device = False
        self.__audio_playing = False


    def is_expect_speech(self):
        return __avs.is_expect_speech()


    def recording(self):
        state = self.__device_state.get_state()
        if state == DeviceState.IDLE or state == DeviceState.EXPECTING_SPEECH:
            self.__device_state.set_state(DeviceState.RECOGNIZING)

            print("[STATE:DEVICE] recording started 3  seconds")
            time.sleep(3.0)
            print("[STATE:DEVICE] recording end")
            audio = self.recorder.get_data()
            self.__avs.put_audio(audio)

            self.__device_state.set_state(DeviceState.BUSY)


    def send_audio(self, audio):
        self.__device_state.set_state(DeviceState.BUSY)
        self.__avs.put_audio(audio)



    # this method run on the avs's thread
    def play(self, audio):
        if audio is not None:
            with open("response.mp3", 'w') as f:
                f.write(audio)
            cmd = "mpg321 -q %s1sec.mp3 %sresponse.mp3" % (self.__path, self.__path)
            subprocess.call(cmd.strip().split(' '))

        if self.__avs.is_expect_speech():
            self.__device_state.set_state(DeviceState.EXPECTING_SPEECH)
            self.recording()
        else:
            self.__device_state.set_state(DeviceState.IDLE)
            self.recorder.set_detection_state(True)


    def stop(self):
        self.__avs.close()
