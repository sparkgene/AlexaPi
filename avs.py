#! /usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from hyper import HTTP20Connection
import json
import threading
from creds import *


class Avs:
  ENDPOINT = 'avs-alexa-na.amazon.com'

  def __init__(self):
    self.downstram_stop_signal = threading.Event()
    self.connection = HTTP20Connection(host=self.ENDPOINT, secure=True, force_proto='h2', enable_push=True)
    self.establish_downstream()
    self.synchronize_to_avs()

  def establish_downstream(self):
    header = {"Authorization": "Bearer %s" % (self.gettoken())}
    self.downstream_id = self.connection.request(method="GET", url=self.__interface("directives"), headers=header)
    downstream_response = self.connection.get_response(downstream_id)
    if downstream_response.status != 200:
      raise NameError("Bad downstream response %s" % (downstream_response.status))
    self.downstream_boundary = get_downstream_boundary(response)
    downstream_polling = threading.Thread(target=self.downstram_polling_thread)
    downstream_polling.start()

  def synchronize_to_avs(self):
    boundary_name = 'synchronization-term'
    header = self.__header(boundary_name)
    stream_id = conn.request(method="POST", url=self.__interface("events"), headers=header, body=self.__synchronize_message(boundary_name))
    res = conn.get_response(stream_id)
    if res.status != 204:
      raise NameError("Bad synchronize response %s" % (res.status))

  def get_downstream_boundary(self, response):
    content = response.headers.pop('content-type')[0]
    b_start = content.find(b'boundary=')
    b_end = content[b_start:].find(b';')
    if b_end == -1:
        boundary = content[b_start+9:]
    else:
        boundary = content[b_start+9:b_start+b_end]
    return boundary

  def downstram_polling_thread(self):
    downstream = self.connection.streams[self.downstream_id]

    while self.downstram_stop_signal.is_set():
      if len(downstream.data) > 1:
        new_data, actual_stream.data = read_from_downstream(self.downstream_boundary, actual_stream.data)
        if len(new_data) > 0:
          print("response:" + new_data)
          # message = parse_data(new_data, self.downstream_boundary)
          # self.process_response_handle(message)
      time.sleep(0.5)

  def close(self):
    self.downstram_stop_signal.set()
    self.connection.close()

  def recognize(self):
    boundary_name = 'recognize-term'
    header = self.__header(boundary_name)

    # build and request first message
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
    first_part_body = self.__message_body_second([], recognize_first_message())
    second_part_header = self.__message_header_second(boundary_name)
    second_part_body = self.__message_body_second()

    body = first_part_header + '\n\n' first_part_body + '\n\n' + second_part_header + '\n\n' + second_part_body + '\n\n' + self.__end_boundary()
    r = self.conn.request(method="GET", url=self.__interface("events"), headers=header, body=body)
    print(r)

  def close(self, conn):
    conn.close()

  def gettoken(self):
    payload = {"client_id": Client_ID, "client_secret": Client_Secret, "refresh_token": refresh_token, "grant_type": "refresh_token", }
    url = "https://api.amazon.com/auth/o2/token"
    r = requests.post(url, data=payload)
    resp = json.loads(r.text)
    return resp['access_token']

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
    message += 'Content-type: application/json; charset=UTF-8\n'
    return message

  def __message_body_first(self, contexts, event):
    message = {}
    message["context"] = contexts
    message["event"] = event
    return message

  def __message_header_second(self, name):
    message = ''
    message += self.__begin_boundary(name)
    message += 'Content-Disposition: form-data; name="audio\n'
    message += 'Content-type: application/octet-stream\n'
    return message

  def __message_body_second(self, file):
  	with open('recording.wav') as inf:
  		data = inf.read()
    return data

  def __begin_boundary(self, name):
    return '\n--' + name + '\n'

  def __end_boundary(self, name):
    return '\n--' + name + '--' + '\n'

ContentTypes = {
  "MULTIPART_FORM_DATA": "multipart/form-data",
  "JSON": "application/json",
  "JSON_UTF8": "application/json; charset=UTF-8",
  "AUDIO": "application/octet-stream"
}

HttpHeaders = {
  "CONTENT_TYPE": "Content-Type",
  "CONTENT_DISPOSITION": "Content-Disposition",
  "CONTENT_ID": "Content-ID",
  "AUTHORIZATION": "authorization",
  "Parameters": {
    "BOUNDARY": "boundary",
    "CHARSET": "charset"
  }
}

avs = Avs()
avs.establish()
avs.recognize()
avs.close()
