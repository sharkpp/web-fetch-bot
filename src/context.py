# buildin pacakges
import re
import os
from os import path
# 3rd party packages
import yaml
# my pacakges
from action import BuildinActionKey

"""
webbook-dl context
>> define class related to context
"""

class Context:
  vars = None
  result_vars = None
  action_cmds = None
  registerd_action_list = None
  state = None
  temporaries = None

  def __init__(self, action_cmds):
    self.vars = {}
    self.result_vars = {}
    self.action_cmds = action_cmds
    self.registerd_action_list = set(action_cmds.keys())
    self.state = {}
    self.temporaries = set()

  # 一時利用とマークしたファイルを削除
  def temporaries_cleanup(self):
    base_dirs = set()
    for temporary_path in self.temporaries:
      try:
        os.remove(temporary_path)
        base_dirs.add(path.dirname(temporary_path))
      except OSError as e:
        pass
    for base_dir in base_dirs:
      try:
        os.rmdir(base_dir)
      except OSError as e:
        # 空っぽでなければ削除はされない
        pass
    self.temporaries = set()

  def reset_vars(self):
    """
    一時変数をクリア
    """
    self.result_vars = {}

  def register_vars(self, vars_list):
    """
    変数を登録
    """
    #print(vars_list.keys())
    for name, s in vars_list.items():
      self.vars[name] = self._apply_vars(self.result_vars, s)

  def apply_vars(self, s):
    """
    変数を展開
    """
    return self._apply_vars(self.vars, s)

  def _apply_vars(self, var_list, s):
    """
    変数を置き換え
    """
    if type(s) != str:
      return s
    r = s
    pos_offset = 0
    for m in re.finditer(r"\$(\{([0-9a-zA-Z_.-]+)\}|([0-9a-zA-Z_.-]+))", s, re.MULTILINE):
      var_name = (m.group(2) or m.group(3)).split(".")
      var_value = var_list
      for var_name_token in var_name:
        if var_name_token in var_value:
          var_value = var_value[var_name_token]
        else:
          var_value = ""
          break
      if 0 == m.start(0) and len(s) == m.end(0):
        # １つの変数のみを指定している場合はそのまま埋め込む
        r = var_value
        break
      r = r[:m.start(0)+pos_offset] + str(var_value) + r[m.end(0)+pos_offset:]
      pos_offset += len(str(var_value)) - (m.end(0) - m.start(0))
    return r

  def _exec_actions(self, actions):
    """
    アクションを実行
    """
    for action in actions:
      # アクションを取得
      action_type = None
      for k in set(action.keys()):
        if BuildinActionKey.value_of(k) is not None:
          continue
        if k in self.registerd_action_list:
          action_type = k
          break

      # 名称を印字
      if BuildinActionKey.NAME.value in action:
        print(action[BuildinActionKey.NAME.value], ">>>>>>>>>>>>>>>>>>")

      self.reset_vars()

      # アクション実行
      if action_type is None:
        continue
      action_fn = self.action_cmds[action_type]
      action_success = action_fn(self, action[action_type])
      #print(">>>",action_type,action_success)
      if not action_success:
        # アクションの実行に失敗
        if "skip" != action_type:
          print("{} fail".format(action_type))
        break

      # 変数を作成
      if BuildinActionKey.SET.value in action:
        self.register_vars(action[BuildinActionKey.SET.value])

  def read_state(self, fname):
    """
    DL状態を読み込み
    """
    cur_state = set()
    if fname in self.state:
      cur_state = self.state[fname]
    else:
      cur_state = self.state[fname] = set()
      try:
        with open(fname, mode="r") as file:
          state_raw = yaml.safe_load(file)
          if 1 == state_raw["state"]["version"]:
            cur_state = self.state[fname] = set(state_raw["state"]["done"])
      except Exception as e:
        return cur_state
    return cur_state

  def save_state(self):
    """
    DL状態を保存
    """
    for fname, state in self.state.items():
      with open(fname, mode="w") as f:
        f.write(yaml.dump({
          "state": {
            "version": 1,
            "done": list(state)
          }
        }))

