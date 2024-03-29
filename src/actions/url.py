# buildin pacakges
from datetime import datetime
from urllib.parse import urljoin
import json
import re
import urllib
import math
import traceback
# 3rd party packages
import requests
from requests.exceptions import Timeout
# my pacakges
from libraries.logger import logger

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

UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"

url_match = re.compile("^((GET|POST)\s+)?(https?:\/\/.+)$")

requests.adapters.DEFAULT_RETRIES = 5

def _url(ctx, params):
  #print("_url",params)
  try:
    encoding = None
    cookies = None
    headers = {}
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
      if base_url is not None and "" != base_url:
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
          kk = ctx.apply_vars(k.strip("\""))
          if type(kk) is str:
            if v is not None:
              data[kk] = ctx.apply_vars(v)
            else:
              data[kk] = ""
          elif type(kk) is dict:
            for kkk, vvv in kk.items():
              data[kkk] = vvv
      logger.debug("_url", "method/url", method, url)
      logger.debug("_url", "headers", headers)
      logger.debug("_url", "encoding", encoding)
      logger.debug("_url", "data", data)
  except Exception as e:
    logger.error("_url", traceback.format_exc())
    return False

  #logger.debug("_url",method,url,encoding)
#  if cookies is not None:
#    for i, cookie in enumerate(cookies):
#      logger.debug("<%s>"%(i),cookie)

  reqopts = {
    "timeout": (REQUEST_CONNECT_TIMEOUT, REQUEST_RECV_TIMEOUT),
  }
  headers["User-Agent"] = UA
  if cookies is not None:
    reqopts["cookies"] = cookies
  if 0 < len(headers):
    reqopts["headers"] = headers

  # クッキーを処理するためにリダイレクトを処理する
  reqopts["allow_redirects"] = False

  req = requests.session()
  req.keep_alive = False

  if "GET" == method:
    try:
      response = req.get(
        url, **reqopts
      )
    except Timeout:
      logger.warning("url", url, "timeout")
      return False
  elif "POST" == method:
    # POST内容をコンテント種別ごとに処理を変えて準備
    if data is not None:
      content_Type = headers["Content-Type"].split(";")[0]
      if "application/x-www-form-urlencoded" == content_Type:
        data = urllib.parse.urlencode(data)
      elif "application/json" == content_Type:
        data = json.dumps(data)
      reqopts["data"] = data
    # POST
    try:
      response = req.post(
        url, **reqopts
      )
    except Timeout:
      logger.error("url", url, "timeout")
      return False
  else:
    return False

  if "allow_redirects" in reqopts and \
      False == reqopts["allow_redirects"]:
    # リダイレクトを処理する
    history = []
    if "data" in reqopts:
      del reqopts["data"]
    _url = url
    while 300 == (math.floor(response.status_code / 100) * 100):
      history.append(response)
      history[len(history)-1].request.headers["cookie"] = cookies.get_dict() if cookies is not None else dict()
      if re.search(r"^http:\/\/.+", response.headers["Location"][0]) is None: # 相対URL
        _url = urljoin(_url, response.headers["Location"])
      else: # 絶対URL
        _url = response.headers["Location"]
      logger.debug(">>>",_url)
      logger.debug(">>>",response.cookies.keys())
      logger.debug(">>>",reqopts)
      logger.debug(">>>",reqopts["cookies"].keys() if hasattr(reqopts, "cookies") else None)
      # クッキーを更新する
      if "cookies" not in reqopts:
        cookies = reqopts["cookies"] = response.cookies
      else:
        reqopts["cookies"].update(response.cookies)
      try:
        response = req.get(
          _url, **reqopts
        )
      except Timeout:
        logger.warning(">>>url", url, "timeout")
        return False
      except Exception as err:
        logger.warning(">>>url", url, err)
        return False
      logger.debug(">>>------------")
    response.history = history
    response.request.headers["cookie"] = cookies.get_dict() if cookies is not None else dict()

  if encoding is None:
    if HEADER_CONTENT_TYPE in response.headers:
      m = re.search(r"^(text\/[a-zA-Z0-9.-]+|application\/json)(; *charset\s*=\s*([^;\s]+|.+$))?", response.headers[HEADER_CONTENT_TYPE])
      if m is not None:
        encoding = m.group(3) if m.group(3) is not None else "utf-8"
      else:
        encoding = "binary"

  logger.debug(response.status_code)    # HTTPのステータスコード取得
  logger.debug(response.text[0:64])    # レスポンスのHTMLを文字列で取得
  logger.debug(response.headers)

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

  logger.debug("==========================")
  for i, hist in enumerate(response.history):
    logger.debug('history<'+str(i)+'>.request.url:', hist.request.url)
    logger.debug('history<'+str(i)+'>.request.body:', hist.request.body)
    logger.debug('history<'+str(i)+'>.request.headers:', hist.request.headers)
    logger.debug('history<'+str(i)+'>.status_code:', hist.status_code)
    logger.debug('history<'+str(i)+'>.headers:', hist.headers)
    logger.debug('history<'+str(i)+'>.cookies:', hist.cookies.get_dict())
    logger.debug("--------------------------")
  logger.debug('url:', url)
  logger.debug('response.url:', response.url)
  logger.debug('response.request.url:', response.request.url)
  logger.debug('response.request.body:', response.request.body)
  logger.debug('response.request.headers:', response.request.headers)
  logger.debug('response.status_code:', response.status_code)
  logger.debug('response.headers:', response.headers)
  logger.debug('response.cookies:', response.cookies.get_dict())
  logger.debug('body:', (body if type(body) is str else str(body))[0:1024])
  logger.debug("==========================")

  #if "Set-Cookie" in response.headers:
  #  #logger.debug("Set-Cookie",response.headers["Set-Cookie"])
  #  response.headers["Set-Cookie"] = (
  #    re.sub(r"Domain=.+?(,\s*|$)", "",
  #    re.sub(r"Expires=.+?;\s*", "", 
  #      response.headers["Set-Cookie"]))
  #  )
  #  #logger.debug("Set-Cookie@",response.headers["Set-Cookie"])
  #logger.debug("cookies",(response.cookies))

  # クッキーをマージ
  if cookies is not None:
    response.cookies.update(reqopts["cookies"])

  ctx.result_vars["res"] = {
    "url": url,
    "body": body,
    "status": response.status_code,
    "headers": dict(response.headers),
    "timestamp": content_last_modified_date, # GMT
    "cookies": response.cookies,
    "response_url": response.url,
  }

  return True

def get_actions():
  """
  Returns a list of the actions it is providing
  """
  return {
    "url": _url,
  }
