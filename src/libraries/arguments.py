# buildin pacakges
import argparse
import re
from io import StringIO
from contextlib import redirect_stderr
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
  try:
    with redirect_stderr(err):
      args = parser.parse_args(arguments)
  except:
    print(re.sub(r"^.+?: ", "", err.getvalue().split("\n")[1]) + "\n")
    return None
  return args
