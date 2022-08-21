# buildin pacakges
from contextlib import redirect_stderr
from os import path
from datetime import datetime, timezone
import re
import sys
# 3rd party packages
# my pacakges
from action import load_actions
from context import Context
from recipe import load_recipes
from libraries.exceptions import QuitActionException, AbortActionException
from libraries.mail_client import mail_command
from libraries.system import caffeinate
import libraries.config as config

"""
webbook-dl main
>> application main entry
"""

def print_help():
  print(
"""usage: %s [-h] { <command> ... | URL [ URL ... ] }

ebook download command

default arguments:
  URL            download target url

positional arguments:
  {commit,help}
    commit       see `commit -h`
    help         see `help -h`
 
optional arguments:
  -h, --help     show this help message and exit
""" % (
    sys.argv[0]
  ))

def main():

  config.load("config.yaml")
  
  args = sys.argv[1:]

  if len(args) <= 0:
    print_help()
    return

  if mail_command(args):
    return
  elif re.search(r"^https?:.+", args[0]) is not None:
    download_urls(args)
  else:
    print_help()

def download_urls(urls):

  # load actions & recipes
  SRC_DIR = path.dirname(__file__)
  actions_cmds = load_actions(SRC_DIR)
  recipes = load_recipes(path.join(SRC_DIR, ".."))

  #-------------------------------------------
  # main

  caffeinate()

  # 指定された Url を順に処理
  for url in urls:
    #print("{} ------".format(url))
    # Url にマッチするレシピを探して処理
    for name, recipe in recipes.items():
      ctx = Context(actions_cmds)
      ctx.vars["URL"] = url
      ctx.vars["TITLE"] = recipe.title
      ctx.vars["BASE_DIR"] = recipe.title
      ctx.vars["START_TIME"] = datetime.now(timezone.utc)
      try:
        # Url にレシピがマッチするか
        if recipe.target.search(url) is None:
          continue
        print("{} ========".format(recipe.title))

        # レシピ内のアクションを順に処理
        ctx._exec_actions(recipe.actions)

        # 状態を保存
        ctx.save_state()

        # 一時ファイルをクリーン
        ctx.temporaries_cleanup()

      except QuitActionException as e:
        # 状態を保存
        ctx.save_state()
        # 一時ファイルをクリーン
        ctx.temporaries_cleanup()
        # 指示された場所で終了
        sys.exit()

      except AbortActionException as e:
        # 中断
        sys.exit()

      except Exception as e:
        print(name, e)  

if __name__ == "__main__":
  main()
