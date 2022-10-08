# buildin pacakges
from os import path
import re
import traceback
# 3rd party packages
# my pacakges

"""
actions:
  - include:
      path: common/pdf-download
      in:
        BASE_URL: ${URL}
        BOOK_LIST: ${BOOK_LIST}
"""

PREFIX_INCLUDE_VARIABLE_NAME = "@INCLUDE@"

def _include(ctx, params):
  include_path = ctx.apply_vars(params["path"])
  in_vars = {}
  for name, value in params["in"].items():
    in_vars[name] = ctx.apply_vars(value)
  recipe_dir = path.dirname(ctx.current_recipe.path)
  for part_path, part_recipe in ctx.part_recipes.items():
    check_path = path.splitext(path.relpath(part_path, start=recipe_dir))[0]
    if check_path == include_path:
      #print("part_path*",part_path, part_recipe)
      ctx_ = ctx.clone()
      ctx_.vars = { **ctx_.vars, **in_vars }
      # レシピ内のアクションを順に処理
      ctx_._exec_actions(part_recipe.actions)
      vars_ = {
        key[len(PREFIX_INCLUDE_VARIABLE_NAME):]: value \
          for key, value in ctx_.vars.items() \
            if PREFIX_INCLUDE_VARIABLE_NAME == key[0:len(PREFIX_INCLUDE_VARIABLE_NAME)]
      }
      # 状態を保存
      ctx.state = ctx_.state
      ctx.save_state()
      #print("vars",vars_)
      #print("result_vars",ctx_.result_vars)
      #print("*result_vars",ctx.result_vars)
      ctx.vars = { **ctx.vars, **vars_ }
      break

  return True

def _exports(ctx, params):
  for name in params:
    if name in ctx.vars:
      ctx.vars[PREFIX_INCLUDE_VARIABLE_NAME + name] = ctx.vars[name]
  return True

def get_actions():
  """
  Returns a list of the actions it is providing
  """
  return {
    "include": _include,
    "exports": _exports,
  }
