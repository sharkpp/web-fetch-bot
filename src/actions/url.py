# buildin pacakges
import re
from datetime import datetime
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
    if type(params) is str:
      params = ctx.apply_vars(params)
      m = url_match.fullmatch(params)
      method = (m.group(2) or "GET").upper()
      url = m.group(3)
      encoding = None
    else:
      method = params["method"].upper() if "method" in params else "GET"
      url = ctx.apply_vars(params["url"])
      encoding = params["encoding"] if "encoding" in params else None
  except Exception as e:
    print("_url",e)
    return False

  #print("_url",method,url,encoding)

  if "GET" == method:
    try:
      response = requests.get(\
        url, \
        timeout=(REQUEST_CONNECT_TIMEOUT, \
                  REQUEST_RECV_TIMEOUT)\
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
        encoding = None

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
    "body": body,
    "timestamp": content_last_modified_date # GMT
  }

  return True

def get_actions():
  """
  Returns a list of the actions it is providing
  """
  return {
    "url": _url,
  }
