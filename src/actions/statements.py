# buildin pacakges
import traceback
import re
from copy import deepcopy
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


def my_eval_match(pattern, test):
  return re.search(pattern, test) is not None

def my_eval(ctx, condition):
  cond = ctx.apply_vars(condition)
  # /hoge/ == "hoge" or "hoge" == /hoge/
  # /hoge/ != "hoge" or "hoge" != /hoge/
  cond = re.sub(r"(\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*\')\s*(==|!=)\s*/((?:\\.|[^/\\])*)/", '_match\\2(r"\\3",\\1)', cond)
  cond = re.sub(r"/((?:\\.|[^/\\])*)/\s*(==|!=)\s*(\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*\')", '_match\\2(r\'\\1\',\\3)', cond)
  cond = re.sub(r"_match==", '_match', cond)
  cond = re.sub(r"_match!=", 'not _match', cond)
  #
  return eval(cond, {
      "_match": my_eval_match
    }, ctx.vars)

def _let(ctx, params):
  try:
    for k, v in params.items():
      if "[]" == k[len(k)-2:len(k)]:
        # キーの末尾に [] がついている場合は配列への追加指示とする
        k = k[0:len(k)-2]
        tmp = dict_get_deep(ctx.vars, ctx.apply_vars(k))
        if type(tmp) is not list:
          tmp = []
        tmp.append(deepcopy(ctx.apply_vars(v)))
        dict_set_deep(ctx.vars, ctx.apply_vars(k), tmp)
      else:
        dict_set_deep(ctx.vars, ctx.apply_vars(k), deepcopy(ctx.apply_vars(v)))
  except Exception as e:
    logger.error("_foreach", traceback.format_exc())
    return False
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

def _while(ctx, params):
  try:
    condition = params["condition"]
    do_actions = params["do"]
    while my_eval(ctx, condition):
      ctx._exec_actions(do_actions)

  except ActionException as e:
    raise
  except Exception as e:
    logger.error("_while", traceback.format_exc())
    return False
  return True

def _if(ctx, params):
  try:
    condition = params["condition"]
    then_ = params["then"]
    else_ = params["else"] if "else" in params else []
    elif_ = params["elif"] if "elif" in params else None
    if my_eval(ctx, condition):
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

def _switch(ctx, params):
  try:
    # switch:
    #   var: $HOGE
    #   cases:
    #     - case: "5"
    #       do:
    #         - :
    #     :
    #   default:
    #     do:
    #       - :
    var_ = ctx.apply_vars(params["var"]) \
            if "var" in params and type(params["var"]) is str \
            else None
    cases = params["cases"]
    default_ = params["default"] \
            if "default" in params and \
              type(params["default"]) is dict \
            else None
    #
    case_mached = False
    for case_ in cases:
      condition = case_["case"] + \
                  ("==" + var_ if var_ is not None else "")
      if my_eval(ctx, condition):
        ctx._exec_actions(case_["do"])
        case_mached = True
        break
    if False == case_mached and \
        default_ is not None:
      ctx._exec_actions(default_["do"])

    #print("condition",condition)
    #print("then_",then_)
    #print("else_",else_)
    #print("elselif_e_",elif_)
  except ActionException as e:
    raise
  except Exception as e:
    logger.error("_switch", traceback.format_exc())
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
    "while": _while,
    "if": _if,
    "switch": _switch,
    "print": _print,
    "abort": _abort,
    "quit": _quit,
  }
