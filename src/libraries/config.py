# buildin pacakges
import sys
# 3rd party packages
import yaml
# my pacakges
from libraries.util import dict_get_deep, dict_set_deep

# 設定ファイルパス
config_file_path = None

# 設定内容
config_store = None

def load(fname):
  global config_file_path
  global config_store
  config_file_path = fname
  try:
    with open(config_file_path, mode="r") as f:
      config_store = yaml.safe_load(f)
  except Exception as e:
    config_store = {}
  return True

def save():
  global config_file_path
  global config_store
  if config_store is None:
    return False
  with open(config_file_path, "w") as f:
    yaml.dump(config_store, f)
  return True

def get(name_or_keys, defaultValue=None):
  global config_store
  return dict_get_deep(config_store, name_or_keys, defaultValue)

def set(name_or_keys, value):
  global config_store
  dict_set_deep(config_store, name_or_keys, value)
  save()
  return True
