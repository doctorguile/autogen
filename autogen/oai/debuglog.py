import os
import httpx
import json

import sys

def del_property(obj, key):
  keys = key.split('.')
  for k in keys[:-1]:
    if k.isdigit():  # Check if the key is an index for a list
      k = int(k)
    if isinstance(obj, dict) and k in obj:
      obj = obj[k]
    elif isinstance(obj, list) and k < len(obj):
      obj = obj[k]
    else:
      return  # Key not found, exit function
  if isinstance(obj, dict):
    del obj[keys[-1]]
  elif isinstance(obj, list):
    obj.pop(int(keys[-1]))


def del_properties(obj,
                   keys=["created", "id", "model", "object", "system_fingerprint", "usage", "prompt_filter_results",
                         "choices.0.content_filter_results"]):
  for key in keys:
    del_property(obj, key)



import re


def log_request(request: httpx.Request):
  url = re.sub(r'.*\.openai\.azure\.com', 'openai.azure.com', str(request.url))
  sys.stderr.write(f"// Request: {request.method} {url}\n")
  # print(" Headers:")
  # for key, value in request.headers.items():
  #     print(f"  {key}: {value}")
  if request.content:
    try:
      obj = json.loads(request.content.decode('utf-8'))
      for k in ["model"]:
        if k in obj:
          del obj[k]
      sys.stderr.write(json.dumps(obj, indent=2))
      sys.stderr.write("\n\n")
    except:
      sys.stderr.write(request.content)
      sys.stderr.write("\n\n")


def log_response(response: httpx.Response):
  print(f"Response: {response.status_code} {response.reason_phrase}")
  # print(" Headers:")
  # for key, value in response.headers.items():
  #     print(f"  {key}: {value}")
  if response.content:
    try:
      obj = json.loads(response.text)
      del_properties(obj)
      sys.stderr.write(json.dumps(obj, indent=2))
      sys.stderr.write("\n\n")
    except:
      sys.stderr.write(response.text)
      sys.stderr.write("\n\n")


class LogResponse(httpx.Response):
  def iter_bytes(self, *args, **kwargs):
    for chunk in super().iter_bytes(*args, **kwargs):
      try:
        obj = json.loads(chunk.decode('utf-8'))
        del_properties(obj)
        sys.stderr.write(json.dumps(obj, indent=2))
        sys.stderr.write("\n\n")
      except:
        sys.stderr.write(chunk)
        sys.stderr.write("\n\n")
      yield chunk


class LogTransport(httpx.BaseTransport):
  def __init__(self, transport: httpx.BaseTransport):
    self.transport = transport

  def handle_request(self, request: httpx.Request) -> httpx.Response:
    response = self.transport.handle_request(request)
    return LogResponse(
      status_code=response.status_code,
      headers=response.headers,
      stream=response.stream,
      extensions=response.extensions,
    )


def set_async_logging_http_client(clientkwargs):
    clientkwargs["http_client"] = httpx.AsyncClient(
      transport= LogTransport(httpx.HTTPTransport()),
      event_hooks={
      "request": [log_request],
      # "response": [log_response]
    })

def set_sync_logging_http_client(clientkwargs):
    clientkwargs["http_client"] = httpx.Client(
      transport= LogTransport(httpx.HTTPTransport()),
      event_hooks={
      "request": [log_request],
      # "response": [log_response]
    })


def wrapper(func, **wrapkwargs):
  def inner(*args, **kwargs):
    # Update kwargs with the new values provided in wrapkwargs
    for key, value in wrapkwargs.items():
      kwargs[key] = value
    return func(*args, **kwargs)

  return inner

