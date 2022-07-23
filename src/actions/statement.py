
"""
actions:
  - name: "add "
    action: let
    let:
      LIST:
        - 10
        - 20
  - name: "hoge download, simple"
    action: foreach
    let: I
    in: LIST
    loop:
      - name: "hoge download, simple"
        action: web_read
        params:
          target: https://example.net/hoge/$I
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
    #print("_foreach params",params)
    #print("_foreach in_var",in_var,type(in_var))
    #print("_foreach ctx.vars",ctx.vars.keys())
    #
    for v in in_var:
      ctx.vars[let_var] = v
      ctx._exec_actions(do_actions)
      del ctx.vars[let_var]
  except Exception as e:
    print("_foreach", e)      
    return False
  return True

def get_actions():
  """
  Returns a list of the actions it is providing
  """
  return {
    "let": _let,
    "foreach": _foreach,
  }
