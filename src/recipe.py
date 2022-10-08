# buildin pacakges
from os import walk, path
import re
# 3rd party packages
import yaml
# my pacakges

"""
web-fetch-bot recipe
>> define class and functions related to action
"""

# class define

class Recipe:
  title = None
  target = None
  actions = None
  path = None
  def __init__(self, recipe, path):
    self.title = recipe["title"]
    self.actions = recipe["actions"]
    self.target = re.compile(recipe["target"]) if "target" in recipe else None
    self.path = path

# exports

def load_recipes(recipe_dir, debug=False):
  recipes = {}
  part_recipes = {}
  # load recipes
  for root, dirs, files in walk(recipe_dir, followlinks=True):
    for entry in files:
      if re.fullmatch("^.+\.yaml$", entry) is None:
        continue
      name = path.splitext(entry)[0]
      try:
        full_path = path.abspath(path.join(root, entry))
        with open(full_path, mode="r") as file:
          recipe = Recipe(yaml.safe_load(file), full_path)
          if recipe.target:
            recipes[name] = recipe
            if debug:
              print("recipe: {} <{}> loaded".format(name, recipe.title))
          else:
            part_recipes[full_path] = recipe
            if debug:
              print("recipe<part>: {} <{}> loaded".format(name, recipe.title))
      except Exception as e:
        if debug:
          print("recipe load error: ", entry, e)
        pass

  return recipes, part_recipes
