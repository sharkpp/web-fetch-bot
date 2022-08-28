# buildin pacakges
import unittest
# my pacakges
from common import run_main

class TestActionFor(unittest.TestCase):

    def test_normal_case(self):

        out = run_main("recipes_for")
        out = out.split("\n")

        self.assertEqual("I<class 'int'>: 1" in out, True)
        self.assertEqual("I<class 'int'>: 2" in out, True)
        self.assertEqual("I<class 'int'>: 3" in out, True)
        self.assertEqual("I<class 'int'>: 4" in out, True)
        self.assertEqual("I<class 'int'>: 5" in out, True)

if __name__ == '__main__':
    unittest.main()
