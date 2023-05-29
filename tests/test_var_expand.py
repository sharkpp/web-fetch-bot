# buildin pacakges
import unittest
# my pacakges
from common import MyTestCase, run_main

class TestVarExpand(MyTestCase):

    def test_normal_case(self):

        out = run_main("""
title: fixture for "var expand"
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

    def test_wildcard_case(self):

        out = run_main("""
title: fixture for "var expand wildcard"
actions:
  - let:
      A.x: 10
      A.y: 20
  - let:
      B: ${A.*}
  - print:
    - A.*
    - B.*
    - B
    - "*"
""")
        #print(out)
        out = out.split("\n")

        self.assertEqual("A.*<class 'dict'>: {'x': 10, 'y': 20}" in out, True)
        self.assertEqual("B.*<class 'dict'>: {'x': 10, 'y': 20}" in out, True)
        self.assertEqual("B<class 'dict'>: {'x': 10, 'y': 20}" in out, True)

if __name__ == '__main__':
    unittest.main()
