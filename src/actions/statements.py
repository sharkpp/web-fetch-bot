# buildin pacakges
import traceback
# my pacakges
from libraries.exceptions import ActionException, QuitActionException, AbortActionException
from libraries.util import dict_get_deep, dict_set_deep
from libraries.logger import logger

"""
actions:
  - name: "add "
    let:
      LIST:
        - 10
        - 20
  - name: "hoge download, simple"
    foreach:
      let: I
      in: $LIST
      do:
        - name: "hoge download, simple"
          action: web_read
          params:
            target: https://example.net/hoge/$I
  - name: "for i in 1 ... 5"
    for:
      start: 1
      end: 5
      step: 1
      let: I
      do:
"""

def _let(ctx, params):
  for k, v in params.items():
    dict_set_deep(ctx.vars, ctx.apply_vars(k), ctx.apply_vars(v))
  return True

def _foreach(ctx, params):
  try:
    in_var = ctx.apply_vars(params["in"])
    let_var = params["let"]
    do_actions = params["do"]
    for v in in_var:
      ctx.vars[let_var] = v
      ctx._exec_actions(do_actions)
      del ctx.vars[let_var]
  except ActionException as e:
    raise
  except Exception as e:
    logger.error("_foreach", traceback.format_exc())
    return False
  return True

def _for(ctx, params):
  try:
    start_num = int(ctx.apply_vars(params["start"]))
    end_num = int(ctx.apply_vars(params["end"]))
    step_num = int(ctx.apply_vars(params["step"]) if "step" in params else "1")
    let_var = params["let"]
    do_actions = params["do"]
    for i in range(start_num, end_num + 1, step_num):
      ctx.vars[let_var] = i
      ctx._exec_actions(do_actions)
      del ctx.vars[let_var]
  except ActionException as e:
    raise
  except Exception as e:
    logger.error("_for", traceback.format_exc())
    return False
  return True

def _if(ctx, params):
  try:
    condition = ctx.apply_vars(params["condition"])
    then_ = params["then"]
    else_ = params["else"] if "else" in params else []
    elif_ = params["elif"] if "elif" in params else None
    if eval(condition, {}, ctx.vars):
      ctx._exec_actions(then_)
    else:
      if elif_ is not None and \
          1 < len(elif_) and \
          eval(ctx.apply_vars(elif_[0]), {}, ctx.vars):
        ctx._exec_actions(elif_[1:])
      else:
        ctx._exec_actions(else_)
    #print("condition",condition)
    #print("then_",then_)
    #print("else_",else_)
    #print("elselif_e_",elif_)
  except ActionException as e:
    raise
  except Exception as e:
    logger.error("_if", traceback.format_exc())
    return False
  return True

def _print(ctx, params):
  target = params if params is not None and 0 < len(params) else ctx.vars.keys()
  for k in target:
    v = dict_get_deep(ctx.vars, k)
    if v is not None:
      if type(v) == str and \
          128 < len(v):
        logger.info("{}{}: {}".format(k, type(v), v[:128]))
      else:
        logger.info("{}{}: {}".format(k, type(v), v))
    else:
      logger.info("{}: <None>".format(k))
  return True

def _abort(ctx, params):
  raise AbortActionException()

def _quit(ctx, params):
  raise QuitActionException()

def get_actions():
  """
  Returns a list of the actions it is providing
  """
  return {
    "let": _let,
    "foreach": _foreach,
    "for": _for,
    "if": _if,
    "print": _print,
    "abort": _abort,
    "quit": _quit,
  }
