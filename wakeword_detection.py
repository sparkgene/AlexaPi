import snowboydecoder
import sys
import signal

interrupted = False


def signal_handler(signal, frame):
    global interrupted
    interrupted = True


def interrupt_callback():
    global interrupted
    return interrupted

#models = ["resources/alexa.umdl", "resources/Stop.pmdl"]
models = ["resources/alexa.umdl"]

# capture SIGINT signal, e.g., Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

detector = snowboydecoder.HotwordDetector(models, sensitivity=0.5)
callbacks = [
  lambda: snowboydecoder.play_audio_file(snowboydecoder.DETECT_DING)
  #lambda: snowboydecoder.play_audio_file(snowboydecoder.DETECT_DING)
]
print('Listening... Press Ctrl+C to exit')

# main loop
detector.start(detected_callback=callbacks,
               interrupt_check=interrupt_callback,
               sleep_time=0.03)

detector.terminate()
