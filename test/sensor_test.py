import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN)

while True:
    detect = GPIO.input(18)
    print(detect)
    time.sleep(0.1)
