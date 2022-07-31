# buildin pacakges
from os import path, stat, utime
from datetime import datetime, timezone, timedelta
from sys import version_info

def touch_file(dest, timestamp = None):
  # ファイルのタイムスタンプを指定のものに変更
  sr = stat(path=dest)

  if 3 < version_info.major or \
      (3 == version_info.major and 6 <= version_info.minor):
    local_tz = datetime.now(timezone.utc).astimezone().tzinfo
  else:
    local_tz = datetime.now(timezone(timedelta(0))).astimezone().tzinfo

  if timestamp is None:
    utime(path=dest, times=None)
  else:
    utime(path=dest, times=(sr.st_atime, \
      (timestamp + timestamp.astimezone(local_tz).utcoffset()).timestamp()))
