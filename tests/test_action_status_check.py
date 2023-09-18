# buildin pacakges
import os
import unittest
from os import path
# my pacakges
from common import MyTestCase, run_main, TEMP_DIR

class TestActionStatusCheck(MyTestCase):

    def test_status_check(self):

        out = run_main("""
title: fixture for "status check action"
actions:
  - let:
      BASE_DIR: test
  - skip: test
  - name: OK
    mark.ok: test
  - skip: test
  - name: OK2
    mark.ok: test
""")
        #print("@@@@",out)
        #out = out.split("\n")

        st = os.stat(path.join(TEMP_DIR, "test", "state.yaml"))

        self.assertEqual(st.st_size > 0, True)

    def test_status_check2(self):

        out = run_main("""
title: fixture for "status check action"
actions:
  - let:
      BASE_DIR: test
  - skip: test
  - name: OK
    mark.ok: test
  - skip: test
  - name: OK2
    mark.ok: test
""", sub_dir="fuga")
        #print("@@@@",out)
        #out = out.split("\n")

        st = os.stat(path.join(TEMP_DIR, "fuga", "test", "state.yaml"))

        self.assertEqual(st.st_size > 0, True)

    def test_status_check3(self):

        out = run_main("""
title: fixture for "status check action"
actions:
  - let:
      BASE_DIR: test
  - skip: test
  - skip: test
  - name: OK
    mark.ok: test
  - skip: test
  - name: OK2
    mark.ok: test
""")
        #print("@@@@",out)
        #out = out.split("\n")

        st = os.stat(path.join(TEMP_DIR, "test", "state.yaml"))

        self.assertEqual(st.st_size > 0, True)

    def test_status_check4_deep_subdir(self):

        out = run_main("""
title: fixture for "status check action"
actions:
  - let:
      BASE_DIR: test
  - skip: test
  - name: OK
    mark.ok: test
  - skip: test
  - name: OK2
    mark.ok: test
""", sub_dir="fuga/@過去")
        #print("@@@@",out)
        #out = out.split("\n")

        st = os.stat(path.join(TEMP_DIR, "fuga", "@過去", "test", "state.yaml"))

        self.assertEqual(st.st_size > 0, True)

if __name__ == '__main__':
    unittest.main()
