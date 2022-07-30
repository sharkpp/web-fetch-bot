# buildin pacakges
import json
import re
from enum import Enum
# 3rd party packages
from pyjsparser import parse

"""
actions:
  - name: "json "
    replace:
      in: $HOGE
      out: HOGE
      format: json
    # "{\"test\":\"fuga\"}" -> "{"test": "fuga"}"
"""

def jsToDict(tree):
  r = None
  if "properties" in tree:
    # オブジェクト
    r = {}
    for property in tree["properties"]:
      if "key" not in property or \
          "value" not in property:
        continue
      if "value" in property["value"]:
        r[property["key"]["name"]] = property["value"]["value"]
      elif "elements" in property["value"]:
        r[property["key"]["name"]] = jsToDict(property["value"])
  elif "elements" in tree:
    # 配列
    r = []
    for element in tree["elements"]:
      r.append(jsToDict(element))
  return r


class JsonFormatType(Enum):
  JSON = "json"
  JSONC = "jsonc"
  JS = "js"

def _json_load(ctx, params):
  try:
    in_str = ctx.apply_vars(params["in"])
    out_var = params["out"]
    format = params["format"] if "format" in params else JsonFormatType.JSON.value()
    if JsonFormatType.JSONC.value() == format:
      # /* .. */ や // を削除する
      in_str = re.sub(r'/\*[\s\S]*?\*/|//.*', '', in_str)
      ctx.vars[out_var] = json.loads(in_str)
    elif JsonFormatType.JS.value() == format:
      ctx.vars[out_var] = jsToDict(in_str)
    else:
      ctx.vars[out_var] = json.loads(in_str)
    # フラグを構築
  except Exception as e:
    print("_json_load", e)
    return False
  return True

def get_actions():
  """
  Returns a list of the actions it is providing
  """
  return {
    "json.load": _json_load,
  }
