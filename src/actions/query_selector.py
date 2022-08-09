# buildin pacakges
# 3rd party packages
from bs4 import BeautifulSoup
# my pacakges

"""
actions:
  - name: "add "
    queryselector:
      in: "<title>test</title>"
      selector: "title"
      match_all: False
    set: TITLE
"""

def _query_selector(ctx, params):
  try:
    in_str = ctx.apply_vars(params["in"])
    selector = ctx.apply_vars(params["selector"])
    match_all = params["match_all"] if "match_all" in params else False
    if "<?xml" == in_str[0:5]:
      parser_type = "xml"
    else:
      parser_type = "html.parser"
    soup = BeautifulSoup(in_str, parser_type)
    elms = soup.select(selector)
    matches = []
    for elm in elms:
      if elm is not None:
        attrs = {
          "@tag": elm.tag,
          "@html": elm,
          "@text": elm.get_text(),
        }
        for attr_name in elm.attrs:
          attrs[attr_name] = elm[attr_name]
        matches.append(attrs)
      if not match_all:
        break
    if not match_all:
      ctx.result_vars["match"] = matches[0] if 0 < len(matches) else {}
    else:
      ctx.result_vars["matches"] = matches
  except Exception:
    return False  
  return True

def get_actions():
  """
  Returns a list of the actions it is providing
  """
  return {
    "queryselector": _query_selector,
  }
