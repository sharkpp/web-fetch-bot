# buildin pacakges
import argparse
import re
import sys
from importlib import import_module
from os import scandir, path
# 3rd party packages
import yaml
# my pacakges

# constant define

SRC_DIR = path.dirname(__file__)

# class define

class Recipe:
  title = None
  target = None
  actions = None
  def __init__(self, recipe):
    self.title = recipe["title"]
    self.actions = recipe["actions"]
    self.target = re.compile(recipe["target"])

# load actions
action_cmds = {}
with scandir(path.join(SRC_DIR, "actions")) as it:
  for entry in it:
    if entry.is_file():
      try:
        module = import_module(
          "actions." + path.splitext(entry.name)[0]
        )
        action_cmds.update(module.get_actions())
      except Exception as e:
        print("skip {} by {}".format(entry.name, e))        

# load recipes
recipes = {}
with scandir(path.join(SRC_DIR, "..", "recipes")) as it:
  for entry in it:
    if entry.is_file():
      name = path.splitext(entry.name)[0]
      try:
        with open(path.join(SRC_DIR, "..", "recipes", entry.name)) as file:
          recipes[name] = Recipe(yaml.safe_load(file))
      except Exception as e:
        print(entry.name, e)        

# parse arguments
parser = argparse.ArgumentParser(description="web book downloader")
parser.add_argument("-d", "--debug", action="store_true", help="target urls")
parser.add_argument("urls", metavar="URL", nargs="+", help="target urls")
args = parser.parse_args()

# constant define

BUILDIN_KEY_NAME = "name"
BUILDIN_KEY_SET = "set"
COMMON_ACTION_KEY = set((
  BUILDIN_KEY_NAME,
  BUILDIN_KEY_SET
))

REGISTERD_ACTION_LIST = set(action_cmds.keys())

# class define

class Context:
  vars = None
  result_vars = None

  def __init__(self):
    self.vars = {}
    self.result_vars = {}

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
        if k in COMMON_ACTION_KEY:
          continue
        if k in REGISTERD_ACTION_LIST:
          action_type = k
          break

      # 名称を印字
      if BUILDIN_KEY_NAME in action:
        print(action[BUILDIN_KEY_NAME], ">>>>>>>>>>>>>>>>>>")

      self.reset_vars()
      self.vars["URL"] = url

      #print(">>ctx.vars",self.vars.keys())
      #print(">>",self.result_vars.keys())
      #print("action[BUILDIN_KEY_SET]",action)

      if action_type is None:
        continue

      # アクション実行
      print(">>",action_cmds[action_type])
      action_fn = action_cmds[action_type]
      print("action_fn",action_fn)
      action_fn(self, action[action_type])

      #print("<<ctx.vars",self.vars.keys())
      #print("<<ctx.vars")

      if BUILDIN_KEY_SET in action:
        self.register_vars(action[BUILDIN_KEY_SET])

      #print("<<ctx.vars",self.vars.keys())

# main

#print(args)
#print(actions.keys())
#print(recipes.keys())

for url in args.urls:
  print("{} ------".format(url))
  for name, recipe in recipes.items():
    ctx = Context()
    try:
      if recipe.target.search(url) is None:
        continue
      #print("{} ========".format(name))

      ctx._exec_actions(recipe.actions)

    except Exception as e:
      print(name, e)        