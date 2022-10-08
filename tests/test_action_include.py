# buildin pacakges
import unittest
# my pacakges
from common import run_main

class TestActionInclude(unittest.TestCase):

    def test_normal_case(self):

        out = run_main("recipes_include")
        #print("out-----",out,"------")
        out = out.split("\n")

        self.assertEqual("TEST<class 'str'>: TEST" in out, True)
        self.assertEqual("TEST1<class 'str'>: TEST" in out, True)
        self.assertEqual("TEST2<class 'str'>: TEST2" in out, True)

if __name__ == '__main__':
    unittest.main()
