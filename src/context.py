# buildin pacakges
import re
import os
from copy import deepcopy
from os import path, makedirs
# 3rd party packages
import yaml
# my pacakges
from action import BuildinActionKey
from libraries.logger import logger
from libraries.util import dict_set_deep

"""
web-fetch-bot context
>> define class related to context
"""

class Context:

  def __init__(self, action_cmds, debug=False):
    self.call_level     = 0
    self.debug          = debug
    self.vars           = {}
    self.result_vars    = {}
    self.action_cmds    = action_cmds
    self.registerd_action_list = set(action_cmds.keys())
    self.state          = {}
    self.temporaries    = set()
    self.current_recipe = None
    self.part_recipes   = {}

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
    if type(vars_list) == str:
      # 文字列の場合は $ をもとに設定
      dict_set_deep(self.vars, vars_list, self._apply_vars({**self.vars, **self.result_vars}, "$$"))
    else:
      for name, s in vars_list.items():
        dict_set_deep(self.vars, name, self._apply_vars({**self.vars, **self.result_vars}, s))

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
    # match of
    #   ${abc123}
    #   ${abXX23}
    #   ${AAAA}
    #   ${AAAA.fuga}
    #   ${HOGE.*}
    #   $TEST.x.y
    #   $TEST.*
    #   $TEST*
    #   $$
    for m in re.finditer(r"\$(\{((?:[0-9a-zA-Z_@-]+|\*)(?:\.(?:[0-9a-zA-Z_@-]+|\*))*)\}|((?:[0-9a-zA-Z_@-]+|\*)(?:\.(?:[0-9a-zA-Z_@-]+|\*))*)|\$)", s, re.MULTILINE):
      if "$" == m.group(1):
        var_name = ["$$"]
      else:
        var_name = (m.group(2) or m.group(3)).split(".")
      var_value = var_list
      #logger.debug("var_name",var_name)
      for var_name_token in var_name:
        if "*" == var_name_token:
          r = var_value
          break
        elif  type(var_value) == dict and \
              var_name_token in var_value:
          var_value = var_value[var_name_token]
        elif  type(var_value) == list and \
              0 <= int(var_name_token) and \
              int(var_name_token) < len(var_value):
          var_value = var_value[int(var_name_token)]
        else:
          var_value = ""
          break
      if 0 == m.start(0) and len(s) == m.end(0):
        # １つの変数のみを指定している場合はそのまま埋め込む
        r = var_value
        break
      var_value_ = str(var_value) if var_value is not None else ""
      r = r[:m.start(0)+pos_offset] + var_value_ + r[m.end(0)+pos_offset:]
      pos_offset += len(var_value_) - (m.end(0) - m.start(0))
    #logger.debug("r",r if type(r) is str else type(r))
    return r

  def _exec_actions(self, actions):
    """
    アクションを実行
    """
    self.call_level += 1
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
        name = self.apply_vars(action[BuildinActionKey.NAME.value])
        name = name if name is not None else ""
        logger.info("".join([">"] * self.call_level) + " " + name)

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
          logger.warning("{} fail".format(action_type))
        break

      # 変数を作成
      if BuildinActionKey.SET.value in action:
        self.register_vars(action[BuildinActionKey.SET.value])
    self.call_level -= 1

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
      print("save_state",fname)
      base_dir = path.dirname(fname)
      if 0 < len(base_dir) and not path.exists(base_dir):
        makedirs(base_dir)
      with open(fname, mode="w") as f:
        f.write(yaml.dump({
          "state": {
            "version": 1,
            "done": sorted(list(state))
          }
        }))

  def clone(self):

    tmp_current_recipe, self.current_recipe = self.current_recipe, None
    tmp_action_cmds, self.action_cmds = self.action_cmds, {}
    tmp_registerd_action_list, self.registerd_action_list = self.registerd_action_list, {}
    tmp_temporaries, self.temporaries = self.temporaries, set()
    tmp_part_recipes, self.part_recipes = self.part_recipes, {}

    ctx_ = deepcopy(self)

    self.current_recipe = tmp_current_recipe
    ctx_.current_recipe = tmp_current_recipe
    self.action_cmds = tmp_action_cmds
    ctx_.action_cmds = tmp_action_cmds
    self.registerd_action_list = tmp_registerd_action_list
    ctx_.registerd_action_list = tmp_registerd_action_list
    self.temporaries = tmp_temporaries
    self.part_recipes = tmp_part_recipes
    ctx_.part_recipes = tmp_part_recipes

    return ctx_
