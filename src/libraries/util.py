

# 辞書型からキーを辿り値を取得する
def dict_get_deep(store, name_or_keys, defaultValue=None):
  if type(store) is not dict:
    return None
  if type(name_or_keys) is list:
    name_tokens = name_or_keys
  else:
    # ドットで分割して潜る
    name_tokens = name_or_keys.split(".")
  # 順番に辿って値を取得
  value = store
  for name_token in name_tokens:
    if value is not None and\
       name_token in value:
      value = value[name_token]
    else:
      value = defaultValue
      break
  return value

# 辞書型からキーを辿り値を設定する
def dict_set_deep(store, name_or_keys, data):
  if store is None:
    return
  if type(name_or_keys) is list:
    name_tokens = name_or_keys
  else:
    # ドットで分割して潜る
    name_tokens = name_or_keys.split(".")
  value = store
  value_stack = [ store ]
  names_stack = [ None ]
  for name_token in name_tokens:
    value = value_stack[len(value_stack)-1]
    if type(value) not in [list, dict]:
      value = value_stack[len(value_stack)-2][names_stack[len(value_stack)-1]] = {}
      value_stack[len(value_stack)-1] = value
    if name_token.isdecimal() and \
        type(value) is list and \
        int(name_token) < len(value):
      name_token = int(name_token)
    elif name_token not in value:
      value_stack[len(value_stack)-1][name_token] = {}
      value = value_stack[len(value_stack)-1]
    value_stack.append(value[name_token])
    names_stack.append(name_token)
  value_stack[len(value_stack)-2][names_stack[len(value_stack)-1]] = data
