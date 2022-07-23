# buildin pacakges
from enum import Enum
from importlib import import_module
from os import scandir, path
# 3rd party packages
# my pacakges

"""
webbook-dl action
>> define constants and functions related to action
"""

# constant define

# exports

action_cmds = None

class BuildinActionKey(Enum):
  NAME = "name"
  SET = "set"

  @classmethod
  def value_of(cls, value):
    for e in BuildinActionKey:
      if e.value == value:
        return e
    return None

def load_actions(base_dir):
  action_cmds = {}
  # load actions
  with scandir(path.join(base_dir, "actions")) as it:
    for entry in it:
      if entry.is_file():
        try:
          module = import_module(
            "actions." + path.splitext(entry.name)[0]
          )
          action_cmds.update(module.get_actions())
        except Exception as e:
          print("skip {} by {}".format(entry.name, e))        
  return action_cmds
