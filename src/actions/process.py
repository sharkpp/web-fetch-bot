# buildin pacakges
from os import makedirs, path
import re
import traceback
import subprocess
# 3rd party packages
# my pacakges
from libraries.logger import logger

"""
actions:
  - name: "add "
    exec:
      command: ./hoge
      args:
        - a
        - b
        - c
    set:
      r: $stdout
"""

def _exec(ctx, params):
  try:
    command = ctx.apply_vars(params["command"])
    args = params["args"]
    if type(args) is str:
      args = [
        ctx.apply_vars(m[2])
        for m in re.finditer(r"(\"?)([^ ]+|[^\"]+)\1 ?", args)
      ]
    else:
      args = [
        ctx.apply_vars(str(arg))
          for arg in args
      ]
    timeout = params["timeout"] if "timeout" in params else None
    cwd = ctx.apply_vars(params["cwd"]) if "cwd" in params else path.dirname(ctx.current_recipe.path)

    if 0 < len(cwd) and not path.exists(cwd):
      makedirs(cwd)

    logger.debug("command",command)
    logger.debug("args",args)

    r = subprocess.run(
        tuple(list([command]) + args),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        cwd=cwd,
        timeout=timeout,
        check=False, text=True
      )
    #logger.debug(r)
    ctx.result_vars["stdout"] = r.stdout
    ctx.result_vars["stderr"] = r.stderr

  except Exception as e:
    logger.error("_exec", traceback.format_exc())
    return False
  return True

def get_actions():
  """
  Returns a list of the actions it is providing
  """
  return {
    "exec": _exec,
  }
