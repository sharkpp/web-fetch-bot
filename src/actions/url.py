# buildin pacakges
import re
# 3rd party packages
import requests
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
    response = requests.get(url)
  else:
    return False

  if 200 != response.status_code:
    return False

  if encoding is None:
    if "Content-Type" in response.headers:
      m = re.search(r"^(text\/[a-zA-Z0-9.-]+|application\/json)(; *charset\s*=\s*([^;\s]+|.+$))?", response.headers["Content-Type"])
      if m is not None:
        encoding = m.group(3) if m.group(3) is not None else "utf-8"
      else:
        encoding = None

  #print(response.status_code)    # HTTPのステータスコード取得
  #print(response.text)    # レスポンスのHTMLを文字列で取得

  body = response.text
  if encoding is not None:
    if "binary" == encoding:
      body = response.content
    else:
      body = response.content.decode(encoding)

  ctx.result_vars["res"] = {
    "body": body
  }

  return True

def get_actions():
  """
  Returns a list of the actions it is providing
  """
  return {
    "url": _url,
  }
