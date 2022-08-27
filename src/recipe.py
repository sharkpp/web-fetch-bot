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

def load_recipes(recipe_dir, debug=False):
  recipes = {}
  # load recipes
  for root, dirs, files in walk(recipe_dir, followlinks=True):
    for entry in files:
      if re.fullmatch("^.+\.yaml$", entry) is None:
        continue
      name = path.splitext(entry)[0]
      try:
        with open(path.join(root, entry), mode="r") as file:
          recipes[name] = Recipe(yaml.safe_load(file))
          if debug:
            print("recipe: {} <{}> loaded".format(name, recipes[name].title))
      except Exception as e:
        if debug:
          print("recipe load error: ", entry, e)
        pass

  return recipes
