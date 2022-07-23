# buildin pacakges
from os import makedirs, path
import re

"""
actions:
  - name: check stat
    skip:
      key: hoge
      path: hoge_dir/
  # ^ load state from hoge_dir/state.yaml
  - name: check stat
    skip:
      key: hoge
      path: hoge_dir/fuga.yaml
  # ^ load state from hoge_dir/fuga.yaml
  - name: check stat
    skip: hoge
  # ^ load state from $BASE_DIR/state.yaml
  - name: set state
    ok: hoge
  - name: set state
    fail: hoge
"""

"""
state.yaml file format
|state
|  version: 1
|  done:
|    - hoge
|    - fuga
"""

DEFAULT_STATE_FILENAME = "state.yaml"

def get_state_params(ctx, params):
  x = type(params)
  if isinstance(params, str):
    key = ctx.apply_vars(params)
    state_path = path.join(ctx.vars["BASE_DIR"], DEFAULT_STATE_FILENAME)
  else:
    key = ctx.apply_vars(params["key"])
    # 取得ステータスファイルのパスを生成
    path_ = params["path"] if "path" in params else None
    if path_ is None:
      state_path = path.join(ctx.vars["BASE_DIR"], DEFAULT_STATE_FILENAME)
    else:
      if re.fullmatch(".+/$", path_) is not None:
        state_path = path.join(path_, DEFAULT_STATE_FILENAME)
      else:
        state_path = path_
  return (state_path, key)

def _skip(ctx, params):
  (state_path, key) = get_state_params(ctx, params)
  cur_state = ctx.read_state(state_path)
  if key in cur_state:
    return False
  return True

def _mark_ok(ctx, params):
  (state_path, key) = get_state_params(ctx, params)
  cur_state = ctx.read_state(state_path)
  cur_state.add(key)
  return True

def _mark_fail(ctx, params):
  (state_path, key) = get_state_params(ctx, params)
  cur_state = ctx.read_state(state_path)
  cur_state.discard(key)
  return True

def get_actions():
  """
  Returns a list of the actions it is providing
  """
  return {
    "skip": _skip,
    "mark.ok": _mark_ok,
    "mark.fail": _mark_fail,
  }
