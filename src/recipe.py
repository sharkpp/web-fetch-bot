# buildin pacakges
from os import walk, path
import re
# 3rd party packages
import yaml
# my pacakges
from libraries.logger import logger

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

  def __init__(self, recipe, path_):
    if recipe is None:
      raise ValueError
    self.title = recipe["title"] \
      if "title" is not recipe \
      else path.splitext(path.basename(path_))[0]
    self.actions = recipe["actions"]
    self.path = path_
    self.target = None
    if "target" in recipe:
      self.target = []
      for target in (
          recipe["target"] \
            if type(recipe["target"]) is list \
            else [ recipe["target"] ]
          ):
        self.target.append(re.compile(target))

  def match(self, url):
    for target in self.target:
      if target.search(url) is not None:
        return True
    return False


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
              logger.info("recipe: {} <{}> loaded".format(name, recipe.title))
          else:
            part_recipes[full_path] = recipe
            if debug:
              logger.info("recipe<part>: {} <{}> loaded".format(name, recipe.title))
      except Exception as e:
        if debug:
          logger.warning("recipe load failed: ", entry, e)
        pass

  return recipes, part_recipes
