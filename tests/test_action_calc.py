# buildin pacakges
import unittest
# my pacakges
from common import MyTestCase, run_main

class TestActionCalc(MyTestCase):

    def test_normal_case(self):

        out = run_main("""
title: fixture for "calc action"
actions:
  - let:
      A: 10
      B: 20
  - calc:
      expr: "$A + $B"
    set: C
  - print:
    - C

  - calc:
      expr: "$A*($B+$C)"
    set: D
  - print:
    - D

  - calc:
      expr: "2022-09-02 14:42:22.784901+00:00 + 1.5s"
    set: E
  - print:
    - E

  - calc:
      expr: "2022-09-02 14:42:22.784901+00:00 - 10min"
    set: F
  - print:
    - F
""")
        #print(out)
        out = out.split("\n")

        self.assertEqual("C<class 'int'>: 30" in out, True)
        self.assertEqual("D<class 'int'>: 500" in out, True)
        self.assertEqual("E<class 'datetime.datetime'>: 2022-09-02 14:42:24.284901+00:00" in out, True)
        self.assertEqual("F<class 'datetime.datetime'>: 2022-09-02 14:32:22.784901+00:00" in out, True)

if __name__ == '__main__':
    unittest.main()
