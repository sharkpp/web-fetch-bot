# buildin pacakges
import unittest
# my pacakges
from common import run_main

class TestActionIf(unittest.TestCase):

    def test_normal_case(self):

        out = run_main("recipes_if")
        print(out)
        out = out.split("\n")

        self.assertEqual("RES1<class 'int'>: 1" in out, True)
        self.assertEqual("RES2<class 'int'>: 2" in out, True)
        self.assertEqual("RES3<class 'int'>: 1" in out, True)
        self.assertEqual("RES3<class 'int'>: 2" in out, True)
        self.assertEqual("RES3<class 'int'>: 3" in out, True)

if __name__ == '__main__':
    unittest.main()
