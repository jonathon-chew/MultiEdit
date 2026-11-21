import sys

import Adonis
from pyflags.flag import Flags

def cli() -> Flags | None:
    flag = Flags()
    flag.add(["--before", "-b"], "What is it now", str, required=True)
    flag.add(["--after", "-a"], "What would you like it to be", str, required=True)
    flag.add(["--cwd", "-c"], "What is the starting dir you want to walk through", str, default=".")
    flag.add(["--ignore", "-i"], "Any files or dirs to skip", list[str], default=[])
    flag.add(["--search", "-s"], "Just search for the string", bool)
    flag.add(["--dry-run", "-d"], "just print what you would change, don't actually change it", bool)
    flag.add(["--show-errors", "-se"], "ignore errors, don't print to the screen", bool, default=True)

    flag.add(["--help", "-h"], "show the possible commands and their helper text", bool, default=False)
    flag.add(["--version", "-V"], "show the version number", bool, default=False)
    flag.add(["--verbose", "-v"], "print everything possible to the screen", bool, default=True)
    # flag.add(["--quiet", "-q"], "don't print anything to the screen", bool)

    if len(sys.argv) > 1:
        Adonis.PrintInfo("Parsing from command line arguments...")
        flag.parse_and_resolve(sys.argv[1:])

        if flag.help or flag.version:
            if flag.help:
                help_test = flag.help_text_ordered()
                assert isinstance(help_test, str)
                Adonis.PrintInfo(help_test)
                exit(0)
            else:
                Adonis.PrintInfo("0.3.1")
            sys.exit(0)
        return flag
    else:
        # TODO: impliment
        """ Adonis.PrintInfo("Parsing from stdin...")
        sys.stdin """
        pass