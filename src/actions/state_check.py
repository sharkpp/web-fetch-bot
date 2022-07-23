
"""
actions:
  - name: check stat
    skip: hoge
  - name: set state
    ok: hoge
  - name: set state
    fail: hoge
"""

def _skip(ctx, params):
  return False

def _mark_ok(ctx, params):
  return False

def _mark_fail(ctx, params):
  return False

def get_actions():
  """
  Returns a list of the actions it is providing
  """
  return {
    "skip": _skip,
    "mark.ok": _mark_ok,
    "mark.fail": _mark_fail,
  }
