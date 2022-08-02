# buildin pacakges
import sys
import subprocess
import atexit
from time import sleep

proc_caffeinate = None

def caffeinate():

  if "darwin" in sys.platform:
      proc_caffeinate = subprocess.Popen("caffeinate")

  def cleanup():
    if proc_caffeinate:
      proc_caffeinate.terminate()

  atexit.register(cleanup)
