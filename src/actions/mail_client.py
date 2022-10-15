# buildin pacakges
import re
import math
import traceback
from time import sleep
from datetime import datetime, timezone, timedelta
# 3rd party packages
# my pacakges
from libraries.mail_client import read
from libraries.util import dict_get_deep, dict_set_deep
from libraries.logger import logger

"""
Mail client action

actions:
  - name: "add "
    mail.read:
      mail_address: hoge@example.net
      read_num: 10
      read_interval: 5000
      read_query: "hoge"
      match:
        subject: /hoge/
        body: /code: ([0-9]+)/
        headers.Return-Path: /.+/
      timeout: 30000
    set:
      code: ${body.1}
"""

def _mail_read(ctx, params):
  try:
    mail_address = ctx.apply_vars(params["mail_address"])
    read_wait = params["read_wait"] if "read_wait" in params else 1000
    timeout = params["timeout"] if "timeout" in params else 30000
    match = {
      k: ctx.apply_vars(v) for k, v in params["match"].items()
    }
    read_opts = { "flat": True }
    if "read_num" in params:
      read_opts["max_read"] = params["read_num"] 
    if "read_query" in params:
      read_opts["q"] = ctx.apply_vars(params["read_query"])
    if "read_start" in params:
      read_opts["start_time"] = ctx.apply_vars(params["read_start"])
    #
    message_ids = set()
    time_limit = (
      datetime.now(timezone.utc) + 
      timedelta(
        weeks=0,
        days=   math.floor(timeout / 1000 / 60 / 60 / 24),
        hours=  math.floor(timeout / 1000 / 60 / 60) % 24,
        minutes=math.floor(timeout / 1000 / 60     ) % 60,
        seconds=math.floor(timeout / 1000          ) % 60,
        milliseconds=timeout % 1000, microseconds=0
      )
    )
    sleep(5) # メール受信まで適当に遅延させる
    while datetime.now(timezone.utc) < time_limit:

      messages = read(mail_address, **read_opts)
      logger.debug("messages", len(messages) if messages is not None else -1)
      if messages is not None:
        for message in messages:
          message_id = message["message_id"][0]
          # 処理ずみをスキップし、そうでないものを処理する
          if message_id not in message_ids:
            result_vars = {}
            message_ids.add(message_id)
            not_matches_count = 0
            logger.debug("------------------")
            logger.debug("message",message)
            for match_target_key, match_pattern in match.items():
              match_target_values = dict_get_deep(message, match_target_key)
              for match_target_value in match_target_values:
                m = re.fullmatch(r"/(.+?)/([is]?)", match_pattern)
                logger.debug("~~~~~~~~~~~~~~~~~~~")
                logger.debug("m",m,match_pattern)
                if m is not None:
                  # フラグを構築
                  flags = 0
                  if 0 < m.group(2).find("i"):
                    flags |= re.IGNORECASE
                  elif 0 < m.group(2).find("s"):
                    flags |= re.DOTALL
                  # パターンマッチ
                  mm = re.search(m.group(1), match_target_value, flags)
                  logger.debug("mm",mm,m.group(1), match_target_value, flags)
                  if mm is not None:
                    logger.debug("mm>",mm.group(0),mm.groups())
                    not_matches_count -= 1
                    #result_vars["{}".format(match_target_key)] = match_target_value
                    dict_set_deep(result_vars, match_target_key.split(".")+["0"], mm.group(0))
                    for groupIndex, groupValue in enumerate(mm.groups()):
                      dict_set_deep(result_vars, match_target_key.split(".")+[str(groupIndex + 1)], groupValue)
                else:
                  pass
                not_matches_count += 1
            # 結果確認
            logger.debug("not_matches_count",not_matches_count)
            if 0 == not_matches_count:
              ctx.result_vars = result_vars
              time_limit = datetime.now(timezone.utc)
              break

      # 次回取得待ち
      sleep(read_wait / 1000)

  except Exception as e:
    logger.error("_mail_read", traceback.format_exc())
    return False

  return 0 < len(ctx.result_vars)

def get_actions():
  """
  Returns a list of the actions it is providing
  """
  return {
    "mail.read": _mail_read,
  }
