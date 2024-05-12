# buildin pacakges
import re
import traceback
# my pacakges
from libraries.format import format
from libraries.logger import logger

"""
actions:
  - name: "add "
    replace:
      in: $HOGE
      old: /pet (store)/
      new: dog ${1}
    set: HOGE
    # "hoge pet store in" -> "hoge dog store in"
  - name:
    format:
      in: $I
      format: "000'.jpg'"
    set: PAGE_FILENAME
"""


def _replace(ctx, params):
  try:
    in_str = ctx.apply_vars(params["in"])
    flags_ = params["flags"] if "flags" in params else ""
    old_str = params["old"]
    old_re = params["old"].strip("/")
    new_str = params["new"] # キャプチャは ${99} 形式
    # フラグを構築
    flags = re.MULTILINE
    if 0 < flags_.find("i"):
      flags |= re.IGNORECASE
    elif 0 < flags_.find("s"):
      flags |= re.DOTALL
    # 置換処理
    if old_str != old_re:
      # 正規表現で置換
      new_str = re.sub(r"\$\{([0-9]+)\}|\$([0-9]+)", "\\\\\\1\\2", new_str)
      new_str = ctx.apply_vars(new_str)
      s = re.sub(old_re, new_str, in_str)
      ctx.result_vars["$$"] = \
        ctx.apply_vars(s)
    else:
      # テキストを置換
      ctx.result_vars["$$"] = \
        ctx.apply_vars(in_str.replace(ctx.apply_vars(old_str), new_str))
  except Exception as e:
    logger.error("_replace", traceback.format_exc())
    return False
  return True

def _format(ctx, params):
  # https://docs.microsoft.com/ja-jp/office/vba/language/reference/user-interface-help/format-function-visual-basic-for-applications
  try:
    in_str = ctx.apply_vars(params["in"])
    format_ = params["format"]
    ctx.result_vars["$$"] = format(format_, in_str)
  except Exception as e:
    logger.error("_format", traceback.format_exc())
    return False
  return True

def _html_entity_decode(ctx, params):
  try:
    in_ = ctx.apply_vars(params["in"])
    ctx.result_vars["$$"] = (in_
      .replace('&nbsp;', ' ')
      .replace('&quot;', '"')
      .replace('&lt;',   '<')
      .replace('&gt;',   '>')
      .replace('&amp;',  '&')
    )
  except Exception as e:
    logger.error("_html_entity_decode", traceback.format_exc())
    return False
  return True

def _join(ctx, params):
  try:
    in_ = ctx.apply_vars(params["in"])
    sep_ = ctx.apply_vars(params["sep"])
    ctx.result_vars["$$"] = sep_.join(in_)
  except Exception as e:
    logger.error("_html_entity_decode", traceback.format_exc())
    return False
  return True

def get_actions():
  """
  Returns a list of the actions it is providing
  """
  return {
    "replace": _replace,
    "format": _format,
    "html_entity.decode": _html_entity_decode,
    "join": _join,
  }
