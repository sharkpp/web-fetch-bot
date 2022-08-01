
class ActionException(Exception):
  pass

class QuitActionException(ActionException):
  pass

class AbortActionException(ActionException):
  pass
