# buildin pacakges
from os import makedirs, path
# 3rd party packages
# my pacakges

"""
actions:
  - name: "hoge write"
    file.write:
      dest: hoge.txt
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
  dest = ctx.apply_vars(params["dest"])
  contents = ctx.apply_vars(params["contents"])
  base_dir = path.dirname(dest)
  #保存したいけどどこかでエラーで止まる
  #print("_file_write",base_dir)
  if not path.exists(base_dir):
    makedirs(base_dir)
  with open(dest, mode="w" if "str" == type(contents) else "wb") as f:
      f.write(contents)
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
