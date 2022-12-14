# buildin pacakges
import re
import traceback
# 3rd party packages
# my pacakges
from libraries.logger import logger

"""
actions:
  - name: "add "
    match:
      /https:\/\/www\.meitetsu\.co\.jp\/wind\/backnumber\/.*?\/index\.html/
    $ if not maches abort action
  - name: "add "
    match:
      condition:
        /https:\/\/www\.meitetsu\.co\.jp\/wind\/backnumber\/.*?\/index\.html/
"""

def _match(ctx, params):
  in_text = ctx.apply_vars(params["in"])
  pattern = ctx.apply_vars(params["pattern"].strip("/"))
  flags_ = params["flags"] if "flags" in params else ""
  out = params["out"] if "out" in params else {}
  match_all = params["match_all"] if "match_all" in params else True
  logger.debug("_match",{"in":in_text[0:1024],"pattern":pattern,"flags":flags_,"out":out,"match_all":match_all})
  # フラグを構築
  flags = re.MULTILINE
  if 0 < flags_.find("i"):
    flags |= re.IGNORECASE
  elif 0 < flags_.find("s"):
    flags |= re.DOTALL
  # パターンマッチ
  matches = []
  for m in re.finditer(pattern, in_text, flags):
    logger.debug("_match",{"m":m})
    # グループを辞書型に
    matches_groups = {}
    for i in range(0, len(m.groups()) + 1):
      matches_groups[str(i)] = m.group(i)
    # マッチした内容を指定された構造に
    match = {**matches_groups}
    for k, v in out.items():
      match[k] = ctx._apply_vars({**matches_groups, **ctx.vars}, v)
    matches.append(match)
  if match_all:
    ctx.result_vars["matches"] = matches
  else:
    ctx.result_vars["match"] = matches[0] if 0 < len(matches) else {}
  return True

def get_actions():
  """
  Returns a list of the actions it is providing
  """
  return {
    "match": _match,
  }
