# buildin pacakges
from datetime import datetime
import traceback
from enum import Enum
# my pacakges
from libraries.logger import logger

"""
actions:
  - strftime:
      format: "%s"
    set: TIMESTAMP
"""

def _strftime(ctx, params):
  try:
    format = ctx.apply_vars(params["format"])
    now = datetime.now()
    ctx.result_vars["$$"] = now.strftime(format)
    # フラグを構築
  except Exception as e:
    logger.error("_strftime", traceback.format_exc())
    return False
  return True

def get_actions():
  """
  Returns a list of the actions it is providing
  """
  return {
    "strftime": _strftime,
  }
