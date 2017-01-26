#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import RPi.GPIO as GPIO
import json
import re
import time
from avs import Avs

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN)


try:
    while True:
        print GPIO.input(18)
        sleep(1)

except KeyboardInterrupt:
        pass

GPIO.cleanup()
