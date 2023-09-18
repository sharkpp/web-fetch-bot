# buildin pacakges
from contextlib import redirect_stderr
from os import makedirs, path, getcwd, chdir
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
  -s, --sub-dir     set sub dir name
""" % (
    sys.argv[0]
  ))

def download_command(params):
  # 引数解析
  args = parse_arguments(params, [
    [ "urls",               { "nargs": "+" } ],
    [ "-v", "--verbose",    { "dest": "verbose", "action": "count", "default": 0 } ],
    [ "-r", "--recipe-dir", { "dest": "recipe_dir" } ],
    [ "-s", "--sub-dir",    { "dest": "sub_dir" } ],
  ])
  # 引数解析結果確認
  #print("args",args)
  if args is None:
    return False
  # ログのレベルを設定
  # -----------------------------
  # logger.*  arg  
  # -----------------------------
  # DEBUG     -vv  args.verbose=2
  # INFO      -v   args.verbose=1
  # WARNING        args.verbose=0
  # ERROR          args.verbose=0
  # CRITICAL       args.verbose=0
  # -----------------------------
  elif 1 < args.verbose:
    logger.setLevel(logger.DEBUG)
  elif 0 < args.verbose:
    logger.setLevel(logger.INFO)
  else:
    logger.setLevel(logger.WARNING)
  # ダウンロード実行
  download_urls(
    args.urls,
    debug=1<args.verbose,
    recipe_dir=args.recipe_dir,
    sub_dir=args.sub_dir
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

def download_urls(urls, debug=False, recipe_dir=None, sub_dir=None):

  # load actions & recipes
  SRC_DIR = path.dirname(__file__)
  actions_cmds = load_actions(SRC_DIR)
  recipes, part_recipes = load_recipes(
    recipe_dir if recipe_dir is not None \
      else path.join(SRC_DIR, "..", "recipes"),
    debug=debug
  )
  # main

  caffeinate()

  cur_dir = getcwd()

  # 指定された Url を順に処理
  for url in urls:
    #print("{} ------".format(url))
    # Url にマッチするレシピを探して処理
    for name, recipe in recipes.items():
      try:
        # Url にレシピがマッチするか
        if not recipe.match(url):
          continue

        # コンテキスト作成
        ctx = Context(actions_cmds, debug=debug)
        ctx.vars["URL"]         = url
        ctx.vars["TITLE"]       = recipe.title
        ctx.vars["BASE_DIR"]    = recipe.title
        ctx.vars["START_TIME"]  = datetime.now(timezone.utc)
        ctx.vars["RECIPE_PATH"] = recipe.path
        ctx.vars["RECIPE_DIR"]  = path.dirname(recipe.path)
        ctx.current_recipe      = recipe
        ctx.part_recipes        = part_recipes

        # 作業ディレクトリを移動(なければ作る)
        cwd = path.join(cur_dir, sub_dir or "")
        try:
          chdir(cwd)
        except FileNotFoundError as e:
          makedirs(cwd)
          chdir(cwd)
        ctx.vars["CWD"]  = cwd

        if debug:
          logger.debug("{} ========".format(recipe.title))

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
        # 作業ディレクトリをもどす
        chdir(cur_dir)
        # 指示された場所で終了
        sys.exit()

      except AbortActionException as e:
        # 作業ディレクトリをもどす
        chdir(cur_dir)
        # 中断
        sys.exit()

      except Exception as e:
        if debug:
          logger.debug(name, e)  

  # 作業ディレクトリをもどす
  chdir(cur_dir)

if __name__ == "__main__":
  main()
