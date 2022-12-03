# buildin pacakges
import unittest
# my pacakges
from common import run_main

class TestActionIf(unittest.TestCase):

    def test_normal_case(self):

        out = run_main("""
title: fixture for "if action"
actions:
  # case 1
  - let:
      V: True
  - if:
      condition: "True == $V"
      then:
        - let:
            RES1: 1
      else:
        - let:
            RES1: 2
  - print:
      - RES1
  # case 2
  - let:
      A.X: False
  - if:
      condition: "True == ${A.X}"
      then:
        - let:
            RES2: 1
      else:
        - let:
            RES2: 2
  - print:
      - RES2
  # case 3
  - for:
      start: 1
      end: 4
      step: 1
      let: I
      do:
        - if:
            condition: "1 == $I"
            then:
              - let:
                  RES3: 1
            elif:
              - "2 == ${I}"
              - let:
                  RES3: 2
            else:
              - let:
                  RES3: 3
        - print:
          - RES3
""")
        #print("----",out,"----")
        out = out.split("\n")

        self.assertEqual("RES1<class 'int'>: 1" in out, True)
        self.assertEqual("RES2<class 'int'>: 2" in out, True)
        self.assertEqual("RES3<class 'int'>: 1" in out, True)
        self.assertEqual("RES3<class 'int'>: 2" in out, True)
        self.assertEqual("RES3<class 'int'>: 3" in out, True)

    def test_regexp_match_case(self):

        out = run_main("""
title: fixture for "if action"
actions:
  - let:
      S1: "abef"
      S2: "abcdef"
      S3: "abbef"
      S4: "ab/xef"
  - if:
      condition: "/ab.+ef/ == '$S1'"
      then:
        - let:
            RES1: 1
  - if:
      condition: "/ab.+ef/ == '$S2'"
      then:
        - let:
            RES2: 1
  - if:
      condition: "/ab.+ef/ == '$S3'"
      then:
        - let:
            RES3: 1
  - if:
      condition: "/ab\\\/.+ef/ == '$S3'"
      then:
        - let:
            RES4: 1
  - if:
      condition: "/ab\\\/.+ef/ == '$S4'"
      then:
        - let:
            RES5: 1
  - print:
      - RES1
      - RES2
      - RES3
      - RES4
      - RES5
""")
        #print("----",out,"----")
        out = out.split("\n")

        self.assertEqual("RES1<class 'int'>: 1" not in out, True)
        self.assertEqual("RES2<class 'int'>: 1" in out, True)
        self.assertEqual("RES3<class 'int'>: 1" in out, True)
        self.assertEqual("RES4<class 'int'>: 1" not in out, True)

if __name__ == '__main__':
    unittest.main()
