# buildin pacakges
from subprocess import run, PIPE, STDOUT
from os import makedirs, path, rmdir
import os
# my pacakges

TEMP_DIR = path.join(path.dirname(__file__), ".tmp")
TEMP_FILE = "tmp.yaml"

def run_main(recipe_or_target, use_fixture_dir=False):

  if use_fixture_dir:
    target = "https://example.net/tests/" + recipe_or_target
  else:
    target = "https://example.net/tests/"

  try:

    recipe_path = path.join(TEMP_DIR, TEMP_FILE)

    if not use_fixture_dir:
      makedirs(TEMP_DIR, exist_ok=True)
      with open(recipe_path, mode="w") as f:
        f.write("target: " + target + "\n" + recipe_or_target)

    r = run(
      [
        "python",
        path.join(path.dirname(__file__), "..", "src", "main.py"),
        "-v",
        "--recipe-dir", TEMP_DIR if not use_fixture_dir else path.join(path.dirname(__file__), "fixtures"),
        target
      ],
      cwd=path.dirname(__file__),
      stdout=PIPE, stderr=STDOUT,
      timeout=10 # sec
    )

    if not use_fixture_dir:
      os.remove(recipe_path)
      rmdir(TEMP_DIR)

    return r.stdout.decode("utf8")

  except:

    return ""

