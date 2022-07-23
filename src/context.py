# buildin pacakges
import re
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

  def __init__(self, action_cmds):
    self.vars = {}
    self.result_vars = {}
    self.action_cmds = action_cmds
    self.registerd_action_list = set(action_cmds.keys())
    self.state = {}

  # 一時変数をクリア
  def reset_vars(self):
    self.result_vars = {}

  # 変数を登録
  def register_vars(self, vars_list):
    #print(vars_list.keys())
    for name, s in vars_list.items():
      self.vars[name] = self._apply_vars(self.result_vars, s)

  # 変数を展開
  def apply_vars(self, s):
    return self._apply_vars(self.vars, s)

  def _apply_vars(self, var_list, s):
    #if "INDEX_BODY" in self.vars:
    #  del self.vars["INDEX_BODY"]
    #print("_apply_vars",var_list,s)
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
      #print("_apply_vars",var_value)
      if 0 == m.start(0) and len(s) == m.end(0):
        #print("@@@@",var_list.keys())
        #print("@@@@",s,var_name,type(var_value),r)
        # １つの変数のみを指定している場合はそのまま埋め込む
        r = var_value
        break
      r = r[:m.start(0)+pos_offset] + var_value + r[m.end(0)+pos_offset:]
      pos_offset += len(var_value) - (m.end(0) - m.start(0))
    #print("_apply_vars @",r)
    return r

  def _exec_actions(self, actions):
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

      #print(">>ctx.vars",self.vars.keys())
      #print(">>",self.result_vars.keys())
      #print("action[BUILDIN_KEY_SET]",action)

      if action_type is None:
        continue

      # アクション実行
      print(">>",self.action_cmds[action_type])
      action_fn = self.action_cmds[action_type]
      print("action_fn",action_fn)
      action_fn(self, action[action_type])

      #print("<<ctx.vars",self.vars.keys())
      #print("<<ctx.vars")

      if BuildinActionKey.SET.value in action:
        self.register_vars(action[BuildinActionKey.SET.value])

  def read_state(self, fname):
    cur_state = set()
    if fname in self.state:
      cur_state = self.state[fname]
    else:
      cur_state = self.state[fname] = set()
      try:
        with open(fname, mode="r") as file:
          state_raw = yaml.safe_load(file)
          if 1 == state_raw.state.version:
            cur_state = self.state[fname] = set(state_raw.state.done)
      except Exception as e:
        return cur_state
    return cur_state

  def save_state(self):
    for fname, state in self.state.items():
      with open(fname, mode="w") as f:
        f.write(yaml.dump({
          "state": {
            "version": 1,
            "done": list(state)
          }
        }))

