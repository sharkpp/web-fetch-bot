# buildin pacakges
import argparse
import sys
from os import path
# 3rd party packages
# my pacakges
from context import Context
from action import load_actions
from recipe import load_recipes

"""
webbook-dl main
>> application main entry
"""

# load actions & recipes
SRC_DIR = path.dirname(__file__)
actions_cmds = load_actions(SRC_DIR)
recipes = load_recipes(path.join(SRC_DIR, ".."))

# parse arguments
parser = argparse.ArgumentParser(description="web book downloader")
parser.add_argument("-d", "--debug", action="store_true", help="target urls")
parser.add_argument("urls", metavar="URL", nargs="+", help="target urls")
args = parser.parse_args()

#-------------------------------------------
# main

#print(args)
#print(actions.keys())
#print(recipes.keys())

# 指定された Url を順に処理
for url in args.urls:
  print("{} ------".format(url))
  # Url にマッチするレシピを探して処理
  for name, recipe in recipes.items():
    ctx = Context(actions_cmds)
    ctx.vars["URL"] = url
    ctx.vars["TITLE"] = recipe.title
    ctx.vars["BASE_DIR"] = recipe.title
    try:
      # Url にレシピがマッチするか
      if recipe.target.search(url) is None:
        continue
      #print("{} ========".format(name))

      # レシピ内のアクションを順に処理
      ctx._exec_actions(recipe.actions)

    except Exception as e:
      print(name, e)  
