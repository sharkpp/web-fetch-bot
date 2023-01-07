# buildin pacakges
import os
import unittest
from os import path
# my pacakges
from common import MyTestCase, run_main, TEMP_DIR

class TestActionPdf(MyTestCase):

    def test_pdf_from_dir(self):

        out = run_main("""
title: fixture for "pdf action from dir"
actions:
  - pdf.from_dir:
      in: ../fixtures/images
      dest: test.pdf
""")
        #out = out.split("\n")

        st = os.stat(path.join(TEMP_DIR, "test.pdf"))

        self.assertEqual(st.st_size > 200000, True)

    def test_pdf_from_dir2(self):

        os.makedirs(path.join(TEMP_DIR, "fuga"), exist_ok=True)
        out = run_main("""
title: fixture for "pdf action from dir2"
actions:
  - pdf.from_dir:
      in: ../fixtures/images
      dest: test.pdf
""", sub_dir="fuga")
        #out = out.split("\n")

        st = os.stat(path.join(TEMP_DIR, "test.pdf"))

        self.assertEqual(st.st_size > 200000, True)

if __name__ == '__main__':
    unittest.main()
