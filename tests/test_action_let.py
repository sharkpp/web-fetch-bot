# buildin pacakges
import unittest
# my pacakges
from common import run_main

class TestActionLet(unittest.TestCase):

    def test_normal_case(self):

        out = run_main("recipes_let")
        out = out.split("\n")

        self.assertEqual("A<class 'int'>: 10" in out, True)
        self.assertEqual("B<class 'dict'>: {'x': 20}" in out, True)

if __name__ == '__main__':
    unittest.main()
