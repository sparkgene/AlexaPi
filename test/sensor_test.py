import RPi.GPIO as GPIO
import time

while True:
    in = GPIO.input(18)
    print(in)
    time.sleep(0.1)
