import collections
import pyaudio

class RingBuffer(object):
    """Ring buffer to hold audio from PortAudio"""
    def __init__(self, size = 4096):
        self._buf = collections.deque(maxlen=size)

    def extend(self, data):
        """Adds data to the end of buffer"""
        self._buf.extend(data)

    def get(self):
        """Retrieves data from the beginning of buffer and clears it"""
        tmp = bytes(bytearray(self._buf))
        self._buf.clear()
        return tmp


class Recorder(object):
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.stream_in = None
        self.ring_buffer = RingBuffer(80000)
        self.detection_enabled = True

    def get_detection_state(self):
        return self.detection_enabled

    def set_detection_state(self, val):
        self.detection_enabled = val


    def open(self):
        def audio_callback(in_data, frame_count, time_info, status):
            self.ring_buffer.extend(in_data)
            play_data = chr(0) * len(in_data)
            return play_data, pyaudio.paContinue

        if self.stream_in is None:
            stream_in = self.audio.open(
                input=True, output=False,
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                frames_per_buffer=2048,
                stream_callback=audio_callback)
            self.stream_in = stream_in

    def get_data(self):
        return self.ring_buffer.get()

    def stop(self):
        self.stream_in.stop_stream()
        self.stream_in.close()
        self.audio.terminate()
