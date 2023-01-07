# buildin pacakges
import re
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
    if type(timestamp) is str:
      # 文字列の場合は日付が指定されたとして処理する
      for fmt in ([
            "%Y-%m-%d %H:%M:%S",
            "%Y/%m/%d %H:%M:%S",
            "%Y%m%d%H%M%S",
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%Y%m%d",
          ]):
        try:
          timestamp = datetime.strptime(timestamp, fmt)
        except ValueError:
          continue
        break
    utime(path=dest, times=(sr.st_atime, \
      (timestamp + timestamp.astimezone(local_tz).utcoffset()).timestamp()))

def normalize_path(in_):
  in_ = in_.replace('/', '／')
  in_ = in_.replace(':', '：')
  in_ = in_.replace(';', '；')
  in_ = in_.replace('&', '＆')
  in_ = in_.replace('<', '＜')
  in_ = in_.replace('>', '＞')
  in_ = in_.replace('|', '｜')
  in_ = in_.replace('#', '＃')
  in_ = in_.replace('!', '！')
  in_ = in_.replace('?', '？')
  in_ = in_.replace('"', '”')
  in_ = in_.replace('\\', '￥')
  in_ = in_.replace('\.', '￥')
  in_ = re.sub(r'\.+$', '．', in_)
  in_ = re.sub(r'[　 \uE000-\uF8FF]+', ' ', in_)
  in_ = re.sub(r' +$', '', in_)
  return in_
