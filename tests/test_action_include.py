# buildin pacakges
import unittest
# my pacakges
from common import MyTestCase, run_main

class TestActionInclude(MyTestCase):

    def test_normal_case(self):

        out = run_main("recipes_include", use_fixture_dir=True)
        #print("out-----",out,"------")
        out = out.split("\n")

        self.assertEqual("TEST<class 'str'>: TEST" in out, True)
        self.assertEqual("TEST1<class 'str'>: TEST" in out, True)
        self.assertEqual("TEST2<class 'str'>: TEST2" in out, True)

    def test_normal_case2(self):

        out = run_main("recipes_include2", use_fixture_dir=True)
        #print("out-----",out,"------")
        out = out.split("\n")

        self.assertEqual("TEST2<class 'str'>: _202" in out, True)

if __name__ == '__main__':
    unittest.main()
