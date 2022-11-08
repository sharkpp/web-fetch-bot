# buildin pacakges
import unittest
# my pacakges
from common import run_main

class TestActionWhile(unittest.TestCase):

    def test_normal_case(self):

        out = run_main("recipes_while1")
        out = out.split("\n")

        self.assertEqual("I<class 'int'>: 1" in out, True)
        self.assertEqual("I<class 'int'>: 2" in out, True)
        self.assertEqual("I<class 'int'>: 3" in out, True)
        self.assertEqual("I<class 'int'>: 4" in out, True)
        self.assertEqual("I<class 'int'>: 5" in out, False)

    # def test_infinity_case(self):

    #     out = run_main("recipes_while2")
    #     out = out.split("\n")

    #     self.assertEqual("I<class 'int'>: 1" in out, True)
    #     self.assertEqual("I<class 'int'>: 2" in out, True)
    #     self.assertEqual("I<class 'int'>: 3" in out, True)
    #     self.assertEqual("I<class 'int'>: 4" in out, True)
    #     self.assertEqual("I<class 'int'>: 5" in out, False)

if __name__ == '__main__':
    unittest.main()
