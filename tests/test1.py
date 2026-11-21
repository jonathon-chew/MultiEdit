import tempfile
import sys
import unittest

from pyflags.flag import Flags

import src.MultiEdit as me

class MakeEdits(unittest.TestCase):

    def setUp(self) -> None:
        return super().setUp()

    def test_edits(self):

        temp_dir = tempfile.mkdtemp()

        sys.argv.extend(["--before", "bleak", "--after", "peak", "--cwd", f"{temp_dir}"])

        flag = Flags()
        flag.add(["--before", "-b"], "What is it now", str, required=True)
        flag.add(["--after", "-a"], "What would you like it to be", str, required=True)
        flag.add(["--cwd", "-c"], "What is the starting dir you want to walk through", str, default=".")
        flag.add(["--ignore", "-i"], "Any files or dirs to skip", list[str], default=[])
        flag.add(["--search", "-s"], "Just search for the string", bool)
        flag.add(["--dry-run", "-d"], "just print what you would change, don't actually change it", bool)
        flag.add(["--show-errors", "-se"], "ignore errors, don't print to the screen", bool, default=True)

        with open(f"{temp_dir}/example.txt", "w") as w:
            w.write(f"""
            This is bleak
            """)
    

if __name__ == "__main__":
    unittest.main()