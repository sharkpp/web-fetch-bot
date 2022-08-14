# buildin pacakges
import sys
# 3rd party packages
import yaml
# my pacakges

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

def get(name, defaultValue=None):
  global config_file_path
  global config_store
  if config_store is None:
    return None
  # ドットで分割して潜る
  name_tokens = name.split(".")
  store = config_store
  for name_token in name_tokens:
    if name_token in store:
      store = store[name_token]
    else:
      store = defaultValue
      break
  return store

def set(name, value):
  global config_file_path
  global config_store
  if config_store is None:
    return None
  # ドットで分割して潜る
  name_tokens = name.split(".")
  store = config_store
  store_stack = [ config_store ]
  names_stack = [ None ]
  for name_token in name_tokens:
    store = store_stack[len(store_stack)-1]
    if type(store) not in [list, dict]:
      store = store_stack[len(store_stack)-2][names_stack[len(store_stack)-1]] = {}
      store_stack[len(store_stack)-1] = store
    if name_token not in store:
      store_stack[len(store_stack)-1][name_token] = {}
      store = store_stack[len(store_stack)-1]
    store_stack.append(store[name_token])
    names_stack.append(name_token)
  store_stack[len(store_stack)-2][names_stack[len(store_stack)-1]] = value
  return True
