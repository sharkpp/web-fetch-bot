# buildin pacakges
import unittest
# my pacakges
from common import run_main

class TestActionFor(unittest.TestCase):

    def test_normal_case(self):

        out = run_main("""
title: fixture for "for action"
actions:
  - name: "for i in 1 ... 5"
    for:
      start: 1
      end: 5
      step: 1
      let: I
      do:
        - print:
          - I
""")
        out = out.split("\n")

        self.assertEqual("I<class 'int'>: 1" in out, True)
        self.assertEqual("I<class 'int'>: 2" in out, True)
        self.assertEqual("I<class 'int'>: 3" in out, True)
        self.assertEqual("I<class 'int'>: 4" in out, True)
        self.assertEqual("I<class 'int'>: 5" in out, True)

if __name__ == '__main__':
    unittest.main()
