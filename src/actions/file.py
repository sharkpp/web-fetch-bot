# buildin pacakges
from os import makedirs, path, stat, utime
from datetime import datetime, timezone, timedelta
from sys import version_info

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
      encode: utf8
    set:
      FUGA: ${res.contents}
      # ^ set file contents to FUGA variable
      #   decode json to dict type
"""

def _file_write(ctx, params):
  #print("_file_write",params["contents"])
  if "dest" not in params \
      or "contents" not in params:
    return False
  dest = ctx.apply_vars(params["dest"])
  dest = dest\
    .replace('"', "") \
    .replace("\\", "￥") \
    .replace(':', "：") \
    .replace('?', "？") \
    .replace('*', "＊") \
    .replace('<', "＜").replace('>', "＞") \
    .replace('|', "｜")
  contents = ctx.apply_vars(params["contents"])
  timestamp = ctx.apply_vars(params["timestamp"]) if "timestamp" in params else None
  base_dir = path.dirname(dest)
  #保存したいけどどこかでエラーで止まる
  #print("_file_write",base_dir)
  if not path.exists(base_dir):
    makedirs(base_dir)
  with open(dest, mode="w" if str == type(contents) else "wb") as f:
      f.write(contents)
  if timestamp is not None:
    # ファイルのタイムスタンプを指定のものに変更
    sr = stat(path=dest)

    if 3 < version_info.major or \
        (3 == version_info.major and 6 <= version_info.minor):
      local_tz = datetime.now(timezone.utc).astimezone().tzinfo
    else:
      local_tz = datetime.now(timezone(timedelta(0))).astimezone().tzinfo

    utime(path=dest, times=(sr.st_atime, \
      (timestamp + timestamp.astimezone(local_tz).utcoffset()).timestamp()))
  return True

def _file_read(ctx, params):
  return False

def get_actions():
  """
  Returns a list of the actions it is providing
  """
  return {
    "file.write": _file_write,
    "file.read": _file_read,
  }
