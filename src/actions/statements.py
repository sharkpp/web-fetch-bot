# buildin pacakges
import sys
# my pacakges
from libraries.exceptions import ActionException, QuitActionException, AbortActionException

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
      in: LIST
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
    ctx.vars[k] = ctx.apply_vars(v)
  return True

def _foreach(ctx, params):
  try:
    in_var = ctx.vars[params["in"]]
    let_var = params["let"]
    do_actions = params["do"]
    for v in in_var:
      ctx.vars[let_var] = v
      ctx._exec_actions(do_actions)
      del ctx.vars[let_var]
  except ActionException as e:
    raise
  except Exception as e:
    print("_foreach", e)      
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
    print("_for", e)      
    return False
  return True

def _print(ctx, params):
  target = params if params is not None and 0 < len(params) else ctx.vars.keys()
  for k in target:
    if k in ctx.vars:
      v = ctx.vars[k]
      if type(v) == str and \
          128 < len(v):
        print("{}{}: {}".format(k, type(v), v[:128]))
      else:
        print("{}{}: {}".format(k, type(v), v))
    else:
      print("{}: <None>".format(k))
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
    "print": _print,
    "abort": _abort,
    "quit": _quit,
  }
