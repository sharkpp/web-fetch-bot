# buildin pacakges
from subprocess import run, PIPE, STDOUT
from os import path
# my pacakges

def run_main(target):

  url = "https://example.net/tests/" + target

  try:

    r = run(
      [
        "python",
        path.join(path.dirname(__file__), "..", "src", "main.py"),
        "-v",
        "--recipe-dir", path.join(path.dirname(__file__), "fixtures"),
        url
      ],
      cwd=path.dirname(__file__),
      stdout=PIPE, stderr=STDOUT,
      timeout=10 # sec
    )

    return r.stdout.decode("utf8")

  except:

    return ""

