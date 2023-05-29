# buildin pacakges
import unittest
# my pacakges
from common import MyTestCase, run_main

class TestActionLet(MyTestCase):

    def test_normal_case(self):

        out = run_main("""
title: fixture for "let action"
actions:
  - let:
      A: 10
      B.x: 20
  - print:
    - A
    - B
""")
        out = out.split("\n")

        self.assertEqual("A<class 'int'>: 10" in out, True)
        self.assertEqual("B<class 'dict'>: {'x': 20}" in out, True)

    def test_add_case(self):

        out = run_main("""
title: fixture for "let action"
actions:
  - let:
      A: 10
  - let:
      A[]: 20
  - let:
      A[]: 30
  - print:
    - A
""")
        out = out.split("\n")

        self.assertEqual("A<class 'list'>: [20, 30]" in out, True)

if __name__ == '__main__':
    unittest.main()
