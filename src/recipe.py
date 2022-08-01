# buildin pacakges
from os import walk, path
import re
# 3rd party packages
import yaml
# my pacakges

"""
webbook-dl recipe
>> define class and functions related to action
"""

# class define

class Recipe:
  title = None
  target = None
  actions = None
  def __init__(self, recipe):
    self.title = recipe["title"]
    self.actions = recipe["actions"]
    self.target = re.compile(recipe["target"])

# exports

def load_recipes(base_dir):
  recipes = {}
  # load recipes
  base_dir_ = path.join(base_dir, "recipes")
  for root, dirs, files in walk(base_dir_):
    for entry in files:
      if re.fullmatch("^.+\.yaml$", entry) is None:
        continue
      name = path.splitext(entry)[0]
      try:
        with open(path.join(root, entry), mode="r") as file:
          recipes[name] = Recipe(yaml.safe_load(file))
      except Exception as e:
        print(entry, e)

  return recipes
