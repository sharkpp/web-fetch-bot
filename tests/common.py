# buildin pacakges
from subprocess import run, PIPE, STDOUT
from os import makedirs, path, rmdir
from shutil import rmtree
import os
import unittest
# my pacakges

TEMP_DIR = path.join(path.dirname(__file__), ".tmp")
TEMP_FILE = "tmp.yaml"

class MyTestCase(unittest.TestCase):
  
  def __init__(self, methodName='runTest') -> None:
      super().__init__(methodName)

  @classmethod
  def setUpClass(self):
    try:
      rmtree(TEMP_DIR)
    except:
      pass
    makedirs(TEMP_DIR, exist_ok=True)

  @classmethod
  def tearDownClass(self):
    return
    try:
      rmtree(TEMP_DIR)
    except:
      pass

def run_main(recipe_or_target, use_fixture_dir=False, sub_dir=None):

  if use_fixture_dir:
    target = "https://example.net/tests/" + recipe_or_target
  else:
    target = "https://example.net/tests/"

  try:

    opt = []

    if sub_dir is not None and sub_dir != "":
      opt.extend([ "--sub-dir", sub_dir ])

    recipe_path = path.join(TEMP_DIR, TEMP_FILE)

    if not use_fixture_dir:
      with open(recipe_path, mode="w") as f:
        f.write("target: " + target + "\n" + recipe_or_target)

    r = run(
      [
        "python",
        path.join(path.dirname(__file__), "..", "src", "main.py"),
        "-vv",
        "--recipe-dir", TEMP_DIR if not use_fixture_dir else path.join(path.dirname(__file__), "fixtures"),
        *opt,
        target
      ],
      cwd=TEMP_DIR,
      stdout=PIPE, stderr=STDOUT,
      timeout=10 # sec
    )

    return r.stdout.decode("utf8")

  except:

    return ""

