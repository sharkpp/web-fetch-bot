# buildin pacakges
from os import scandir, path
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
  recipes_dir = path.join(base_dir, "recipes")
  with scandir(recipes_dir) as it:
    for entry in it:
      if not entry.is_file():
        continue
      if re.fullmatch("^.+\.yaml$", entry.name) is None:
        continue
      name = path.splitext(entry.name)[0]
      try:
        with open(path.join(recipes_dir, entry.name), mode="r") as file:
          recipes[name] = Recipe(yaml.safe_load(file))
      except Exception as e:
        print(entry.name, e)
  return recipes
