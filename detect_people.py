#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import RPi.GPIO as GPIO
import json
import re
import time
from device import Device

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN)

alexa_device = Device()

try:
    while True:
        detect = GPIO.input(18)
        if detect == 1:
            print("[STATE:HUMAN_DETECT] detected.")
            with open('recording2.wav', 'rb') as inf:
                audio = inf.read()
                alexa_device.send_audio(audio)

                while alexa_device.is_idle() == False:
                    time.sleep(0.5)

        time.sleep(1)

except KeyboardInterrupt:
        pass

GPIO.cleanup()
