# buildin pacakges
import sys

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
    ctx.vars[k] = v
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
      print("i",i)
      ctx.vars[let_var] = i
      ctx._exec_actions(do_actions)
      del ctx.vars[let_var]
  except Exception as e:
    print("_for", e)      
    return False
  return True

def _abort(ctx, params):
  sys.exit()
  return True

def get_actions():
  """
  Returns a list of the actions it is providing
  """
  return {
    "let": _let,
    "foreach": _foreach,
    "for": _for,
    "abort": _abort,
  }
