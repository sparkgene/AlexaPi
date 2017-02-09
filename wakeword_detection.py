import snowboydecoder
import sys
import os
import signal
from device import Device

interrupted = False

TOP_DIR = os.path.dirname(os.path.abspath(__file__))
DETECT_DING = os.path.join(TOP_DIR, "resources/ding.wav")
DETECT_DONG = os.path.join(TOP_DIR, "resources/dong.wav")

alexa_device = Device()
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
    print("[STATE:SNOWBOY] detect alexa")
    alexa_device.recording()


def go_back():
    play_beep(fname=DETECT_DING)
    print("[STATE:SNOWBOY] detect go back")
    direct_send_to_alexa('homecoming.wav')


def go_out():
    play_beep(fname=DETECT_DING)
    print("[STATE:SNOWBOY] detect going out")
    direct_send_to_alexa('go_out.wav')


def stop():
    play_beep(fname=DETECT_DONG)
    if not detector is None:
        detector.terminate()


#models = ["resources/alexa.umdl", "resources/Stop.pmdl"]
models = ["resources/alexa.umdl", "resources/go_back.pmdl", "resources/going_out.pmdl", "resources/Stop.pmdl"]

# capture SIGINT signal, e.g., Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

detector = snowboydecoder.HotwordDetector(models, sensitivity=0.5)
callbacks = [alexa, go_back, go_out, stop]
print('Listening... Press Ctrl+C to exit')

# main loop
detector.start(detected_callback=callbacks,
               interrupt_check=interrupt_callback,
               sleep_time=0.03)
