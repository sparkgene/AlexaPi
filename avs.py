#! /usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from hyper import HTTP20Connection
import json
import threading
from creds import *
import time
from Queue import Queue


class Avs:
  ENDPOINT = 'avs-alexa-na.amazon.com'

  def __init__(self, recorder_callback, audio_player_callback):

    def create_connection():
      self.connection = HTTP20Connection(host=self.ENDPOINT, secure=True, force_proto='h2', enable_push=True)
      print("[STATE:INIT] Connection created.")

    def establish_downstream():
      header = {"Authorization": "Bearer %s" % (self.gettoken())}
      self.downstream_id = self.connection.request(method="GET", url=self.__interface("directives"), headers=header)
      downstream_response = self.connection.get_response(self.downstream_id)
      if downstream_response.status != 200:
        raise NameError("Bad downstream response %s" % (downstream_response.status))
      self.downstream_boundary = self.get_boundary(downstream_response)
      print("[STATE:INIT] downstream established. bounday=%s" % (self.downstream_boundary))

      self.stop_signal = threading.Event()
      downstream_polling = threading.Thread(target=self.downstram_polling_thread)
      downstream_polling.start()
      print("[STATE:INIT] downstream polling start")

    def synchronize_to_avs():
      boundary_name = 'synchronization-term'
      header = self.__header(boundary_name)
      stream_id = self.connection.request(method="POST", url=self.__interface("events"), headers=header, body=self.__synchronize_message(boundary_name))
      res = self.connection.get_response(stream_id)
      if res.status != 204:
        raise NameError("Bad synchronize response %s" % (res.status))
      print("[STATE:INIT] synchronize to AVS succeeded.")

    self.audio_player_callback = audio_player_callback
    self.recorder_callback = recorder_callback
    self.voice_queue = Queue()
    self.access_token = None

    create_connection()
    establish_downstream()
    synchronize_to_avs()
    
  def start(self):
    print(["start"])
    th = threading.Thread(target=self.check_audio_arrival)
    th.start()
  
  def get_boundary(self, response):
    content = response.headers.pop('content-type')[0]
    b_start = content.find(b'boundary=')
    b_end = content[b_start:].find(b';')
    if b_end == -1:
        boundary = content[b_start+9:]
    else:
        boundary = content[b_start+9:b_start+b_end]
    return boundary

  def downstram_polling_thread(self):

    def read_from_downstream(boundary, data):
      matching_indices = [n for n, chunk in enumerate(data) if chunk.endswith(boundary)]
      if not matching_indices:
          return b'', data
      boundary_index = matching_indices[-1]

      new_data = data[:boundary_index+1]
      data = data[boundary_index+1:]
      return b''.join(new_data), data

    downstream = self.connection.streams[self.downstream_id]

    while self.stop_signal.is_set() == False:
      if len(downstream.data) > 1:
        new_data, downstream.data = read_from_downstream(self.downstream_boundary, downstream.data)
        if len(new_data) > 0:
          print("response:" + new_data)
      time.sleep(0.5)

  def put_audio(self, audio):
    print("[STATE:AUDIO_PUT] audio arrival")
    self.voice_queue.put(audio)
    print(self.voice_queue.empty())

  def check_audio_arrival(self):
    while self.stop_signal.is_set() == False:
      if self.voice_queue.empty() == False:
        print("[STATE:AUDIO_ARRIVAL] detected autio arrival")
        audio = self.voice_queue.get()
        rf = open('recording.wav', 'w')
        rf.write(audio)
        rf.close()
        self.recognize()
      time.sleep(0.5)

  def recognize(self):
    boundary_name = 'recognize-term'
    header = self.__header(boundary_name)

    def recognize_first_message():
      message = {
              "header": {
                  "namespace": "SpeechRecognizer",
                  "name": "Recognize",
                  "messageId": "1",
                  "dialogRequestId": "1"
              },
              "payload": {
                  "profile": "CLOSE_TALK",
                  "format": "AUDIO_L16_RATE_16000_CHANNELS_1"
              }
      }
      return message

    first_part_header = self.__message_header_first(boundary_name)
    first_part_body = self.__message_body_first([], recognize_first_message())
    second_part_header = self.__message_header_second(boundary_name)
    second_part_body = self.__message_body_second("recording.wav")

    body = first_part_header + '\n' + json.dumps(first_part_body) + '\n' + second_part_header + '\n' + second_part_body + self.__end_boundary(boundary_name)
    stream_id = self.connection.request(method="GET", url=self.__interface("events"), headers=header, body=body)
    print(stream_id)
    res = self.connection.get_response(stream_id)
    if res.status != 200 and res.status != 204:
      print(res.read())
      raise NameError("Bad recognize response %s" % (res.status))

    if res.status == 204:
      print("[STATE:RECOGNIZE] no content")
      print(res.headers)
      print(res.read())
      audio = None
    else:
      print("[STATE:RECOGNIZE] audio response present")
      boundary = self.get_boundary(res)
      response_data = res.read()
      audio = self.pick_up_audio_from_directives(boundary, response_data)
    
    self.play(audio)


  def play(self, audio):
    if self.audio_player_callback is not None:
      self.audio_player_callback(audio)
    else:
      print("[STATE:RECOGNIZE] play device not assigned")

  def recording(self):
    if self.recorder_callback is not None:
      self.recorder_callback()
    else:
      print("[STATE:RECOGNIZE] recording device not assigned")

  def pick_up_audio_from_directives(self, boundary, data):
    chunks = data.split('--' + boundary)
    content_and_attachment = [p for p in chunks if p != b'--' and p != b'--\r\n' and len(p) != 0 and p != '\r\n']
    if len(content_and_attachment) != 2:
      raise NameError("Bad response data")
    return content_and_attachment[1].split('\r\n\r\n')[1].rstrip('\r\n')

  def close(self):
    self.stop_signal.set()
    self.connection.close()

  def gettoken(self):
    if self.access_token is None or (time.mktime(time.gmtime()) - self.token_refreshed_time) > 3570:
      payload = {"client_id": Client_ID, "client_secret": Client_Secret, "refresh_token": refresh_token, "grant_type": "refresh_token", }
      url = "https://api.amazon.com/auth/o2/token"
      r = requests.post(url, data=payload)
      resp = json.loads(r.text)
      self.access_token = resp['access_token']
      self.token_refreshed_time = time.mktime(time.gmtime())
      return resp['access_token']
    else:
      self.access_token

  def __synchronize_message(self, name):
    header = self.__message_header_first(name)
    events = {
      "header": {
        "namespace": "System",
        "name": "SynchronizeState",
        "messageId": "1"
      },
      "payload": {
      }
    }
    body = self.__message_body_first([], events)
    message = header + '\n\n' + json.dumps(body) + '\n\n' + self.__end_boundary(name)
    return message

  def __interface(self, name):
    return "/v20160207/%s" % (name)

  def __header(self, boundary):
    bearer = "Bearer %s" % (self.gettoken())
    content_type = "multipart/form-data; boundary=%s" % (boundary)
    header = {"Authorization": bearer, "content-type": content_type}
    return header

  def __message_header_first(self, name):
    message = ''
    message += self.__begin_boundary(name)
    message += 'Content-Disposition: form-data; name="metadata"\n'
    message += 'Content-Type: application/json; charset=UTF-8\n'
    return message

  def __message_body_first(self, contexts, event):
    message = {}
    message["context"] = contexts
    message["event"] = event
    return message

  def __message_header_second(self, name):
    message = ''
    message += self.__begin_boundary(name)
    message += 'Content-Disposition: form-data; name="audio"\n'
    message += 'Content-Type: application/octet-stream\n'
    return message

  def __message_body_second(self, file):
    with open(file, "rb") as inf:
      data = inf.read()
    return data

  def __begin_boundary(self, name):
    return '\n--' + name + '\n'

  def __end_boundary(self, name):
    return '\n--' + name + '--' + '\n'
