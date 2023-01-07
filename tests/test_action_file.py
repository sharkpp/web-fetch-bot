# buildin pacakges
import os
import unittest
from os import path
# my pacakges
from common import MyTestCase, run_main, TEMP_DIR

class TestActionFile(MyTestCase):

    def test_file_write(self):

        out = run_main("""
title: fixture for "file action write"
actions:
  - file.write:
      dest: hoge.txt
      contents:
        test
""")
        #out = out.split("\n")

        st = os.stat(path.join(TEMP_DIR, "hoge.txt"))

        self.assertEqual(st.st_size, 4)

    def test_file_write2_subdir(self):

        out = run_main("""
title: fixture for "file action write2"
actions:
  - file.write:
      dest: hoge.txt
      contents:
        test
""", sub_dir="fuga")
        #out = out.split("\n")

        st = os.stat(path.join(TEMP_DIR, "fuga", "hoge.txt"))

        self.assertEqual(st.st_size, 4)

    def test_file_read(self):

        with open(path.join(TEMP_DIR, "hoge2.txt"), "w") as f:
            f.write("fugafuga")

        out = run_main("""
title: fixture for "file action read"
actions:
  - file.read:
      src: hoge2.txt
      encoding: utf-8
    set: A
  - print:
    - A
""")
        out = out.split("\n")

        self.assertEqual("A<class 'str'>: fugafuga" in out, True)

    def test_file_read2_subdir(self):

        os.makedirs(path.join(TEMP_DIR, "fuga"), exist_ok=True)
        with open(path.join(TEMP_DIR, "fuga", "hoge3.txt"), "w") as f:
            f.write("fugafuga")

        out = run_main("""
title: fixture for "file action read"
actions:
  - file.read:
      src: hoge3.txt
      encoding: utf-8
    set: A
  - print:
    - A
""", sub_dir="fuga")
        out = out.split("\n")

        self.assertEqual("A<class 'str'>: fugafuga" in out, True)

if __name__ == '__main__':
    unittest.main()
