import sys
import os
import wave
import pyaudio
import time
import signal
import snowboydecoder
from device import Device
from recorder import Recorder
import RPi.GPIO as GPIO

interrupted = False

TOP_DIR = os.path.dirname(os.path.abspath(__file__))
DETECT_DING = os.path.join(TOP_DIR, "resources/ding.wav")
DETECT_DONG = os.path.join(TOP_DIR, "resources/dong.wav")

WAKEWORD_DETECT_PIN = 4    # GPIO 4
WAKEWORD_WAITING_PIN = 17  # GPIO 17

recorder = None
alexa_device = None
detector = None


def signal_handler(signal, frame):
    global interrupted
    interrupted = True


def interrupt_callback():
    global interrupted
    return interrupted


def play_beep(fname=DETECT_DING):
    ding_wav = wave.open(DETECT_DING, 'rb')
    ding_data = ding_wav.readframes(ding_wav.getnframes())
    audio = pyaudio.PyAudio()
    stream_out = audio.open(
        format=audio.get_format_from_width(ding_wav.getsampwidth()),
        channels=ding_wav.getnchannels(),
        rate=ding_wav.getframerate(), input=False, output=True)
    stream_out.start_stream()
    stream_out.write(ding_data)
    time.sleep(0.2)
    stream_out.stop_stream()
    stream_out.close()
    audio.terminate()

def setup_gpio():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(WAKEWORD_DETECT_PIN, GPIO.OUT)
    GPIO.setup(WAKEWORD_WAITING_PIN, GPIO.OUT)
    print("[GPIO] Setup done")

def show_waiting_wakeword():
    print("[GPIO:4] OFF")
    print("[GPIO:17] ON")
    GPIO.output(WAKEWORD_WAITING_PIN, True)
    GPIO.output(WAKEWORD_DETECT_PIN, False)

def show_detect_wakeword():
    print("[GPIO:4] ON")
    GPIO.output(WAKEWORD_DETECT_PIN, True)

def direct_send_to_alexa(wav_file=None):
    with open(wav_file, 'rb') as inf:
        audio = inf.read()
    alexa_device.send_audio(audio)


def alexa():
    show_detect_wakeword()
    play_beep(fname=DETECT_DING)
    print("[STATE:WAKE] detected alexa")
    recorder.set_detection_state(False)
    alexa_device.recording()
    show_waiting_wakeword()


def stop():
    show_waiting_wakeword()
    play_beep(fname=DETECT_DONG)
    print("[STATE:WAKE] detected stop")
    if not detector is None:
        detector.terminate()
        alexa_device.stop()
        recorder.stop()


recorder = Recorder()
models = [
    "resources/alexa.umdl",
    "resources/Stop.pmdl"]
callbacks = [alexa, stop]
detector = snowboydecoder.HotwordDetector(models, sensitivity=0.5, recorder=recorder)
alexa_device = Device(recorder=recorder)

try:
    setup_gpio()
    show_waiting_wakeword()
    # main loop
    detector.start(detected_callback=callbacks,
                   interrupt_check=interrupt_callback,
                   sleep_time=0.03)
except KeyboardInterrupt:
    print("ctrl-c")
except:
    import traceback
    traceback.print_exc()
finally:
    detector.terminate()
    alexa_device.stop()
    recorder.stop()
    GPIO.cleanup()
