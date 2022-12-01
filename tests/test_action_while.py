# buildin pacakges
import unittest
# my pacakges
from common import run_main

class TestActionWhile(unittest.TestCase):

    def test_normal_case(self):

        out = run_main("""
title: fixture for "while action"
actions:

  - let:
      I: 0
  - name: "while"
    while:
      condition: "$I < 5"
      do:
        - print:
            - I
        - calc:
            expr: "$I + 1"
          set: I
""")
        out = out.split("\n")

        self.assertEqual("I<class 'int'>: 1" in out, True)
        self.assertEqual("I<class 'int'>: 2" in out, True)
        self.assertEqual("I<class 'int'>: 3" in out, True)
        self.assertEqual("I<class 'int'>: 4" in out, True)
        self.assertEqual("I<class 'int'>: 5" in out, False)

#     def test_infinity_case(self):

#         out = run_main("""
# title: fixture for "while action 2"
# actions:
#   - let:
#       J: 0
#   - name: "while"
#     while:
#       condition: "$J != -1"
#       do:
#         - print:
#             - J
#         - calc:
#             expr: "$J + 1"
#           set: J
# """)
#         out = out.split("\n")

#         self.assertEqual("I<class 'int'>: 1" in out, True)
#         self.assertEqual("I<class 'int'>: 2" in out, True)
#         self.assertEqual("I<class 'int'>: 3" in out, True)
#         self.assertEqual("I<class 'int'>: 4" in out, True)
#         self.assertEqual("I<class 'int'>: 5" in out, False)

if __name__ == '__main__':
    unittest.main()
