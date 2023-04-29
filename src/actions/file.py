# buildin pacakges
from os import makedirs, path, stat, utime
import json
import traceback
import re
# 3rd party packages
import yaml
# my pacakges
from libraries.file_util import touch_file, normalize_path
from libraries.logger import logger

"""
actions:
  - name: "hoge write"
    file.write:
      dest: hoge.txt
      timestamp: $HOGE
      contents: 
        hoge $FUGA
  - name: "hoge write"
    file.write:
      dest: hoge.txt
      contents: 
        hoge $FUGA
      encode: utf8
  - name: "hoge read"
    file.read:
      src: hoge.json
      type: json
      encoding: utf8
    set: FUGA
      # ^ set file contents to FUGA variable
      #   decode json to dict type
"""

def _file_write(ctx, params):
  #print("_file_write",params["contents"])
  if "dest" not in params \
      or "contents" not in params:
    logger.error("_file_write",params)
    return False
  dest_path = ctx.apply_vars(params["dest"])
  #dest_path = normalize_path(dest_path)
  contents = ctx.apply_vars(params["contents"])
  timestamp = ctx.apply_vars(params["timestamp"]) if "timestamp" in params else None
  is_temporary = True if "temporary" in params and True == params["temporary"] else False
  base_dir = path.dirname(dest_path)
  #保存したいけどどこかでエラーで止まる
  if 0 < len(base_dir) and not path.exists(base_dir):
    makedirs(base_dir)
  with open(dest_path, mode="w" if str == type(contents) or dict == type(contents) else "wb") as f:
    if dict == type(contents):
      f.write(json.dumps(contents))
    else:
      f.write(contents)
  if timestamp is not None:
    # ファイルのタイムスタンプを指定のものに変更
    touch_file(dest_path, timestamp)
  if is_temporary:
    ctx.temporaries.add(dest_path)
  return True

def _file_read(ctx, params):
  src_path = ctx.apply_vars(params["src"])
  type_ = params["type"] if "type" in params else "binary"
  encoding = params["encoding"] if "encoding" in params else "binary"
  #
  try:
    data = None
    print(type_)
    with open(src_path, mode="rb") as file:
      if "json" == type_:
        data = json.load(file)
      elif "yaml" == type_:
        data = yaml.safe_load(file)
      elif "binary" == encoding:
        data = file.read()
      else:
        data = file.read().decode(encoding)
    ctx.result_vars["$$"] = data
  except Exception as e:
    logger.error("_file_read", traceback.format_exc())
  return True

def _path_normalize(ctx, params):

  if type(params) is str:
    in_ = ctx.apply_vars(params)
  else:
    in_ = ctx.apply_vars(params["in"])

  ctx.result_vars["$$"] = normalize_path(in_)

  return True

def get_actions():
  """
  Returns a list of the actions it is providing
  """
  return {
    "file.write": _file_write,
    "file.read": _file_read,
    "path.normalize": _path_normalize,
  }
