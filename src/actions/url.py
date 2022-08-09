# buildin pacakges
from datetime import datetime
from urllib.parse import urljoin
import json
import re
import urllib
# 3rd party packages
import requests
from requests.exceptions import Timeout
# my pacakges

"""
actions:
  - name: "hoge download, simple"
    url:
      url: https://example.net/hoge/epsode
      # ^ set to $CONTENTS variable
    set:
      RES: ${res.body}
    # ^ web content response to RES variable
  - name: "hoge download, by POST method"
    url:
      method: POST
      url: https://example.net/hoge/epsode
      headers:
        Content-Type: application/json
      body:
        hoge:
          fuga: 10
        # send data is '{"hoge":{"fuga":10}}'
    set:
      RES: ${res.body}
      RES_TYPE: ${res.headers.content-type}
"""

REQUEST_CONNECT_TIMEOUT = 10
REQUEST_RECV_TIMEOUT = 60

HEADER_CONTENT_TYPE = "Content-Type"
HEADER_LAST_MODIFIED = "Last-Modified"
HEADER_DATE = "Date"

url_match = re.compile("^((GET|POST)\s+)?(https?:\/\/.+)$")

def _url(ctx, params):
  #print("_url",params)
  try:
    encoding = None
    cookies = None
    headers = None
    data = None
    if type(params) is str:
      params = ctx.apply_vars(params)
      m = url_match.fullmatch(params)
      method = (m.group(2) or "GET").upper()
      url = m.group(3)
    else:
      method = params["method"].upper() if "method" in params else "GET"
      url = ctx.apply_vars(params["url"])
      base_url = ctx.apply_vars(params["base_url"]) if "base_url" in params else None
      if base_url is not None:
        url = urljoin(base_url, url)
      encoding = params["encoding"] if "encoding" in params else None
      cookies = ctx.apply_vars(params["cookies"]) if "cookies" in params else None
      if "headers" in params:
        headers = {}
        for k, v in params["headers"].items():
          if v is not None:
            headers[k] = ctx.apply_vars(v)
          else:
            headers[k] = ""
      if "data" in params:
        data = {}
        for k, v in params["data"].items():
          if v is not None:
            data[k] = ctx.apply_vars(v)
          else:
            data[k] = ""
  except Exception as e:
    print("_url",e)
    return False

  #print("_url",method,url,encoding)

  reqopts = {
    "timeout": (REQUEST_CONNECT_TIMEOUT, REQUEST_RECV_TIMEOUT),
  }
  if cookies is not None:
    reqopts["cookies"] = cookies
  if headers is not None:
    reqopts["headers"] = headers

  if "GET" == method:
    try:
      response = requests.get(
        url, **reqopts
      )
    except Timeout:
      print("url", url, "timeout")
      return False
  elif "POST" == method:
    # POST内容をコンテント種別ごとに処理を変えて準備
    if data is not None:
      data_ = data
      data = {}
      for k, v in data_.items():
        data[ctx.apply_vars(k)] = v
      content_Type = headers["Content-Type"].split(";")[0]
      if "application/x-www-form-urlencoded" == content_Type:
        data = urllib.parse.urlencode(data)
      elif "application/json" == content_Type:
        data = json.dumps(data)
      reqopts["data"] = data
    # POST
    try:
      response = requests.post(
        url, **reqopts
      )
    except Timeout:
      print("url", url, "timeout")
      return False
  else:
    return False

  if 200 != response.status_code:
    return False

  if encoding is None:
    if HEADER_CONTENT_TYPE in response.headers:
      m = re.search(r"^(text\/[a-zA-Z0-9.-]+|application\/json)(; *charset\s*=\s*([^;\s]+|.+$))?", response.headers[HEADER_CONTENT_TYPE])
      if m is not None:
        encoding = m.group(3) if m.group(3) is not None else "utf-8"
      else:
        encoding = "binary"

  #print(response.status_code)    # HTTPのステータスコード取得
  #print(response.text)    # レスポンスのHTMLを文字列で取得
  #print(response.headers)

  # Last-Modified: <day-name>, <day> <month> <year> <hour>:<minute>:<second> GMT
  # >> https://developer.mozilla.org/ja/docs/Web/HTTP/Headers/Last-Modified
  content_last_modified_date = \
    datetime.strptime(response.headers[HEADER_LAST_MODIFIED], "%a, %d %b %Y %H:%M:%S %Z") \
      if HEADER_LAST_MODIFIED in response.headers \
      else None
#  # Date: <day-name>, <day> <month> <year> <hour>:<minute>:<second> GMT
#  # >> https://developer.mozilla.org/ja/docs/Web/HTTP/Headers/Date
#  content_date = \
#    datetime.strptime(response.headers[HEADER_LAST_MODIFIED], "%a, %d %b %Y %H:%M:%S %Z") \
#      if HEADER_LAST_MODIFIED in response.headers \
#      else None

  body = response.text
  if encoding is not None:
    if "binary" == encoding:
      body = response.content
    else:
      body = response.content.decode(encoding)

  ctx.result_vars["res"] = {
    "url": url,
    "body": body,
    "status": response.status_code,
    "headers": dict(response.headers),
    "timestamp": content_last_modified_date, # GMT
    "cookies": response.cookies # GMT
  }

  return True

def get_actions():
  """
  Returns a list of the actions it is providing
  """
  return {
    "url": _url,
  }
