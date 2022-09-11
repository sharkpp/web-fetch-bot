# buildin pacakges
import logging

class MyLogger:

  CRITICAL = logging.CRITICAL
  ERROR    = logging.ERROR
  WARNING  = logging.WARNING
  INFO     = logging.INFO
  DEBUG    = logging.DEBUG
  NOTSET   = logging.NOTSET

  def __init__(self):
    self.stream = logging.StreamHandler()
    self.log = logging.getLogger('web-fetch-bot')
    self.log.addHandler(self.stream)


  def setLevel(self, level):
    self.log.setLevel(level)
    self.stream.setLevel(level)


  def debug(self, *args):
    self.log.debug(" ".join(["%s"] * len(args))%args)

  def info(self, *args):
    self.log.info(" ".join(["%s"] * len(args))%args)

  def warning(self, *args):
    self.log.warning(" ".join(["%s"] * len(args))%args)

  def error(self, *args):
    self.log.error(" ".join(["%s"] * len(args))%args)

  def critical(self, *args):
    self.log.critical(" ".join(["%s"] * len(args))%args)

  def exception(self, *args):
    self.log.exception(" ".join(["%s"] * len(args))%args)

  def log(self, level, msg, *args, **kwargs):
    self.log.log(level, msg, *args, **kwargs)

logger = MyLogger()
