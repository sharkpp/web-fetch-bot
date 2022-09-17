# buildin pacakges
import json
import re
import traceback
from enum import Enum
# 3rd party packages
from pyjsparser import parse
# my pacakges
from libraries.logger import logger

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

def _json_parse(ctx, params):
  try:
    in_str = ctx.apply_vars(params["in"])
    out_var = params["out"]
    format = params["format"] if "format" in params else JsonFormatType.JSON.value()
    if JsonFormatType.JSONC.value == format:
      # /* .. */ や // を削除する
      in_str = re.sub(r'/\*[\s\S]*?\*/|//.*', '', in_str)
      ctx.vars[out_var] = json.loads(in_str)
    elif JsonFormatType.JS.value == format:
      r = parse("const x = " + in_str)
      r = r["body"][0]["declarations"][0]["init"]
      ctx.vars[out_var] = jsToDict(r)
    else:
      ctx.vars[out_var] = json.loads(in_str)
    # フラグを構築
  except Exception as e:
    logger.error("_json_parse", traceback.format_exc())
    return False
  return True

def get_actions():
  """
  Returns a list of the actions it is providing
  """
  return {
    "json.parse": _json_parse,
  }
