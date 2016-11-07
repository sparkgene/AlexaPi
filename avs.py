#! /usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from hyper import HTTP20Connection
import json
from creds import *


class Avs:
  ENDPOINT = 'avs-alexa-na.amazon.com'

  def establish(self):
    conn = HTTP20Connection(host=self.ENDPOINT, secure=True, force_proto='h2')
    boundary_name = 'synchronization-term'
    header = { "Authorization": "Bearer %s" % (self.gettoken()) }
    print(self.__interface("directives") + '\n' + json.dumps(header))
    conn.request(method="GET", url=self.__interface("directives"), headers=header)

    header = self.__header(boundary_name)
    print(self.__interface("events") + '\n' + json.dumps(header) + '\n' + self.__synchronize_message(boundary_name))
    conn.request(method="POST", url=self.__interface("events"), headers=header, body=self.__synchronize_message(boundary_name))
    r = conn.get_response()
    data = r.read()
    print(data)
    return conn

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
    message += 'Content-Disposition: form-data; name="metadata\n'
    message += 'Content-type: application/octet-stream; charset=audio\n'
    return message

  def __message_body_second(self, contexts, event):
    message = {}
    message["context"] = contexts
    message["event"] = event
    return message

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
conn = avs.establish()
conn.close()
