# buildin pacakges
import re
import traceback
from enum import IntEnum
from datetime import datetime, timedelta
# my pacakges
from libraries.logger import logger

"""
actions:
  - let:
      A: 10
      B: 20
  - calc:
      expr: "$A + $B"
    set: C
"""

# '2022-09-02 14:42:22.784901+00:00' にマッチ
#                  <-------------------------------------- 1 --------------------------------------->
MATCH_DATETIME = "([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}\+[0-9]{2}:[0-9]{2})"

# '65.3s' にマッチ
#                   <------- 1 ------->  <----------- 2 ----------->
MATCH_TIMEDELTA = "([0-9]+(?:\.[0-9]+)?)(week|w|sec|s|msec|ms|min|m|hour|h|day|d)"

# 全ての条件を一回で処理
MATCH_PATTERN = "(?:(?:" + ")|(?:".join([
    MATCH_DATETIME,
    MATCH_TIMEDELTA
  ]) + "))"

def _calculation(ctx, params):
  try:
    expr = ctx.apply_vars(params["expr"])
    # 
    for m in reversed(list(re.finditer(MATCH_PATTERN, expr))):
      (
        datetime_value,
        timedelta_value, timedelta_unit
      ) = m.groups()
      # '2022-09-02 14:42:22.784901+00:00' -> 'datetime.fromisoformat('2022-09-02 14:42:22.784901+00:00')'
      if datetime_value is not None:
        expr = expr[0:m.start(0)] + "datetime.fromisoformat('" + datetime_value + "')" + expr[m.end(0):]
      # 65.3s -> timedelta(seconds=5, milliseconds=3, minutes=1)
      elif timedelta_value is not None:
        # ぜんぶ msec に揃える
        n = 0
        if "ms" == timedelta_unit or "msec" == timedelta_unit:
          n = float(timedelta_value)
        elif "s" == timedelta_unit or "sec" == timedelta_unit:
          n = float(timedelta_value) * 1000
        elif "m" == timedelta_unit or "min" == timedelta_unit:
          n = float(timedelta_value) * 1000 * 60
        elif "h" == timedelta_unit or "hour" == timedelta_unit:
          n = float(timedelta_value) * 1000 * 60 * 60
        elif "d" == timedelta_unit or "day" == timedelta_unit:
          n = float(timedelta_value) * 1000 * 60 * 60 * 24
        elif "w" == timedelta_unit or "week" == timedelta_unit:
          n = float(timedelta_value) * 1000 * 60 * 60 * 24 * 7
        args = []
        args.append("weeks="        + str(int(n // (1000 * 60 * 60 * 24 * 7)       )))
        args.append("days="         + str(int(n // (1000 * 60 * 60 * 24    ) %    7)))
        args.append("hours="        + str(int(n // (1000 * 60 * 60         ) %   24)))
        args.append("minutes="      + str(int(n // (1000 * 60              ) %   60)))
        args.append("seconds="      + str(int(n // (1000                   ) %   60)))
        args.append("milliseconds=" + str(int(n                              % 1000)))
        expr = expr[0:m.start(0)] + "timedelta(" + ",".join(args) + ")" + expr[m.end(0):]
    #
    r = eval(expr, {
        "datetime": datetime,
        "timedelta": timedelta
      }, {})
    ctx.result_vars["$$"] = r
    #print(expr, r)
  except Exception as e:
    logger.error("_calculation", expr, traceback.format_exc())
    return False

  return True

def get_actions():
  """
  Returns a list of the actions it is providing
  """
  return {
    "calc": _calculation,
  }
