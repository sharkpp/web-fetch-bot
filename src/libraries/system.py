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
    global proc_caffeinate
    if proc_caffeinate is not None:
      proc_caffeinate.terminate()

  atexit.register(cleanup)
