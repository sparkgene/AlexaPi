#!/usr/bin/env python

import collections
import pyaudio
import snowboydetect
import time
import wave
import os
import logging
import RPi.GPIO as GPIO
from device import Device

logging.basicConfig()
logger = logging.getLogger("snowboy")
logger.setLevel(logging.INFO)
TOP_DIR = os.path.dirname(os.path.abspath(__file__))

RESOURCE_FILE = os.path.join(TOP_DIR, "resources/common.res")

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN)

class HotwordDetector(object):
    def __init__(self, decoder_model,
                 resource=RESOURCE_FILE,
                 sensitivity=[],
                 audio_gain=1,
                 recorder=None):

        tm = type(decoder_model)
        ts = type(sensitivity)
        if tm is not list:
            decoder_model = [decoder_model]
        if ts is not list:
            sensitivity = [sensitivity]
        model_str = ",".join(decoder_model)

        self.detector = snowboydetect.SnowboyDetect(
            resource_filename=resource.encode(), model_str=model_str.encode())
        self.detector.SetAudioGain(audio_gain)
        self.num_hotwords = self.detector.NumHotwords()

        if len(decoder_model) > 1 and len(sensitivity) == 1:
            sensitivity = sensitivity*self.num_hotwords
        if len(sensitivity) != 0:
            assert self.num_hotwords == len(sensitivity), \
                "number of hotwords in decoder_model (%d) and sensitivity " \
                "(%d) does not match" % (self.num_hotwords, len(sensitivity))
        sensitivity_str = ",".join([str(t) for t in sensitivity])
        if len(sensitivity) != 0:
            self.detector.SetSensitivity(sensitivity_str.encode())
        self.recorder = recorder
        self.running = True


    def start(self, detected_callback=None,
              interrupt_check=lambda: False,
              sleep_time=0.03,
              sensor_detect_callback=None):

        if interrupt_check():
            logger.debug("detect voice return")
            return

        tc = type(detected_callback)
        if tc is not list:
            detected_callback = [detected_callback]
        if len(detected_callback) == 1 and self.num_hotwords > 1:
            detected_callback *= self.num_hotwords

        assert self.num_hotwords == len(detected_callback), \
            "Error: hotwords in your models (%d) do not match the number of " \
            "callbacks (%d)" % (self.num_hotwords, len(detected_callback))

        logger.debug("detecting...")
        self.recorder.open()

        while self.running:
            if interrupt_check():
                logger.debug("detect voice break")
                break

            detect_from_sensor = 0
            if self.recorder.get_detection_state() == True:
                data = self.recorder.get_data()
                if len(data) == 0:
                    # print("[STATE:SNOWBOY] Nothing is audio.")
                    time.sleep(sleep_time)
                    continue
                ans = self.detector.RunDetection(data)
                detect_from_sensor = GPIO.input(18)
            else:
                ans = 0
            time.sleep(sleep_time)

            if ans == -1:
                message = "Error initializing streams or reading audio data"
            elif ans > 0:
                message = "Keyword " + str(ans) + " detected at time: "
                # message += time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                detected_callback[ans-1]()
            elif detect_from_sensor == 1:
                message = "Sensor detected " + str(ans) + " detected at time: "
                sensor_detect_callback()

            # logger.info(message)

        logger.debug("finished.")


    def terminate(self):
        self.running = False
