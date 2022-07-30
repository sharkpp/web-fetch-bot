# buildin pacakges
import re
# my pacakges
from libraries.format import format

"""
actions:
  - name: "add "
    replace:
      in: $HOGE
      out: HOGE
      old: /pet (store)/
      new: dog ${1}
    # "hoge pet store in" -> "hoge dog store in"
  - name:
    format:
      in: $I
      out: PAGE_FILENAME
      format: "000'.jpg'"
"""


def _replace(ctx, params):
  try:
    in_str = ctx.apply_vars(params["in"])
    out_var = params["out"]
    flags_ = params["flags"] if "flags" in params else ""
    old_str = params["old"]
    old_re = params["old"].strip("/")
    new_str = params["new"]
    # フラグを構築
    flags = re.MULTILINE
    if 0 < flags_.find("i"):
      flags |= re.IGNORECASE
    elif 0 < flags_.find("s"):
      flags |= re.DOTALL
    # 置換処理
    if old_str != old_re:
      # 正規表現で置換
      new_str = re.sub(r"\$\{([0-9]+)\}", "\\1", new_str)
      ctx.vars[out_var] = \
        ctx.apply_vars(re.sub(old_re, new_str, in_str))
    else:
      # テキストを置換
      ctx.vars[out_var] = \
        ctx.apply_vars(in_str.replace(old_str, new_str))
  except Exception as e:
    print("_replace", e)
    return False
  return True

def _format(ctx, params):
  # https://docs.microsoft.com/ja-jp/office/vba/language/reference/user-interface-help/format-function-visual-basic-for-applications
  try:
    in_str = ctx.apply_vars(params["in"])
    out_var = params["out"]
    format_ = params["format"]
    ctx.vars[out_var] = format(format_, in_str)
  except Exception as e:
    print("_for", e)
    return False
  return True

def get_actions():
  """
  Returns a list of the actions it is providing
  """
  return {
    "replace": _replace,
    "format": _format,
  }
