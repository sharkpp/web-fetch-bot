# buildin pacakges
import argparse
import re
import sys
from io import StringIO
from contextlib import redirect_stderr, redirect_stdout
# 3rd party packages
# my pacakges

def parse_arguments(arguments, options):
  # 引数解析
  parser = argparse.ArgumentParser()
  try:
    for option in options:
      name_num = len(option)
      for i, v in enumerate(option):
        if type(v) is not str:
          name_num = i
          break
      parser.add_argument(*option[0:name_num], **option[name_num])
  except:
    return None
  err = StringIO()
  out = StringIO()
  try:
    with redirect_stderr(err), redirect_stdout(out):
      args = parser.parse_args(arguments)
  except:
    # エラー要因を表示
    err_ = err.getvalue()
    if "" != err_:
      print(re.sub(r"^.+?: ", "", (err_+"\n\n").split("\n")[1]) + "\n")
    return None
  return args
