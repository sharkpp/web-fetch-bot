# buildin pacakges
import unittest
# my pacakges
from common import run_main

class TestActionCalc(unittest.TestCase):

    def test_normal_case(self):

        out = run_main("recipes_calc")
        #print(out)
        out = out.split("\n")

        self.assertEqual("C<class 'int'>: 30" in out, True)
        self.assertEqual("D<class 'int'>: 500" in out, True)
        self.assertEqual("E<class 'datetime.datetime'>: 2022-09-02 14:42:24.284901+00:00" in out, True)
        self.assertEqual("F<class 'datetime.datetime'>: 2022-09-02 14:32:22.784901+00:00" in out, True)

if __name__ == '__main__':
    unittest.main()
