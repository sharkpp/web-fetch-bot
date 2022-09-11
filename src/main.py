# buildin pacakges
from contextlib import redirect_stderr
from os import path
from datetime import datetime, timezone
import logging
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
from libraries.arguments import parse_arguments
from libraries.logger import logger
import libraries.config as config

"""
web-fetch-bot main
>> application main entry
"""

def print_help():
  print(
"""usage: %s [-h] { <command> ... | <OPTIONS> URL [ URL ... ] }

web content download command

default arguments:
  URL            download target url

positional arguments:
  {mail,help}
    mail         see `mail -h`
    help         see `help -h`
 
optional arguments:
  -h, --help        show this help message and exit

OPTIONS
  -v*,  --verbose   show verbose messages
  -r, --recipe-dir  set recipe dir
""" % (
    sys.argv[0]
  ))

def download_command(params):
  # 引数解析
  args = parse_arguments(params, [
    [ "urls",               { "nargs": "+" } ],
    [ "-v", "--verbose",    { "dest": "verbose", "action": "count", "default": 0 } ],
    [ "-r", "--recipe-dir", { "dest": "recipe_dir" } ],
  ])
  # 引数解析結果確認
  #print("args",args)
  if args is None:
    return False
  # ログのレベル
  if 1 < args.verbose:
    logger.setLevel(logger.DEBUG)
  elif 0 < args.verbose:
    logger.setLevel(logger.INFO)
  else:
    logger.setLevel(logger.WARNING)
  # ダウンロード実行
  download_urls(
    args.urls,
    debug=1<args.verbose,
    recipe_dir=args.recipe_dir
  )
  return True

def main():

  config.load("config.yaml")
  
  args = sys.argv[1:]

  if len(args) <= 0:
    print_help()
    return

  if mail_command(args):
    return
  elif download_command(args):
    return
  else:
    print_help()

def download_urls(urls, debug=False, recipe_dir=None):

  # load actions & recipes
  SRC_DIR = path.dirname(__file__)
  actions_cmds = load_actions(SRC_DIR)
  recipes = load_recipes(
    recipe_dir if recipe_dir is not None \
      else path.join(SRC_DIR, "..", "recipes"),
    debug=debug
  )

  #-------------------------------------------
  # main

  caffeinate()

  # 指定された Url を順に処理
  for url in urls:
    #print("{} ------".format(url))
    # Url にマッチするレシピを探して処理
    for name, recipe in recipes.items():
      ctx = Context(actions_cmds, debug=debug)
      ctx.vars["URL"] = url
      ctx.vars["TITLE"] = recipe.title
      ctx.vars["BASE_DIR"] = recipe.title
      ctx.vars["START_TIME"] = datetime.now(timezone.utc)
      try:
        # Url にレシピがマッチするか
        if recipe.target.search(url) is None:
          continue
        if debug:
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
        if debug:
          print(name, e)  

if __name__ == "__main__":
  main()
