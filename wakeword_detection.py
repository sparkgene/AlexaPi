import sys
import os
import wave
import pyaudio
import time
import signal
import snowboydecoder
from device import Device
from recorder import Recorder

interrupted = False

TOP_DIR = os.path.dirname(os.path.abspath(__file__))
DETECT_DING = os.path.join(TOP_DIR, "resources/ding.wav")
DETECT_DONG = os.path.join(TOP_DIR, "resources/dong.wav")

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


def direct_send_to_alexa(wav_file=None):
    with open(wav_file, 'rb') as inf:
        audio = inf.read()
    alexa_device.send_audio(audio)


def alexa():
    play_beep(fname=DETECT_DING)
    print("[STATE:WAKE] detected alexa")
    recorder.set_detection_state(False)
    alexa_device.recording()


def go_back():
    play_beep(fname=DETECT_DING)
    print("[STATE:WAKE] detected go back")
    recorder.set_detection_state(False)
    direct_send_to_alexa('resources/homecoming.wav')


def go_out():
    play_beep(fname=DETECT_DING)
    print("[STATE:WAKE] detected going out")
    recorder.set_detection_state(False)
    direct_send_to_alexa('resources/go_out.wav')


def stop():
    play_beep(fname=DETECT_DONG)
    print("[STATE:WAKE] detected stop")
    if not detector is None:
        detector.terminate()
        alexa_device.stop()
        recorder.stop()


def someone_detected():
    play_beep(fname=DETECT_DING)
    recorder.set_detection_state(False)
    direct_send_to_alexa('resources/visitor.wav')


recorder = Recorder()
models = ["resources/alexa.umdl", "resources/go_back.pmdl", "resources/go_out.pmdl", "resources/Stop.pmdl"]
callbacks = [alexa, go_back, go_out, stop]
detector = snowboydecoder.HotwordDetector(models, sensitivity=0.5, recorder=recorder)
alexa_device = Device(recorder=recorder)

# main loop
detector.start(detected_callback=callbacks,
               interrupt_check=interrupt_callback,
               sleep_time=0.03,
               sensor_detect_callback=someone_detected)
