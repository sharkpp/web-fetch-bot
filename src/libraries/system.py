# buildin pacakges
from subprocess import DEVNULL
import sys
import subprocess
import atexit
from time import sleep

proc_caffeinate = None

def caffeinate():
  global proc_caffeinate

  if "darwin" in sys.platform:
      proc_caffeinate = subprocess.Popen(
        "caffeinate",
        stdout=DEVNULL, stderr=DEVNULL
      )

  def cleanup():
    global proc_caffeinate
    if proc_caffeinate is not None:
      proc_caffeinate.terminate()

  atexit.register(cleanup)
