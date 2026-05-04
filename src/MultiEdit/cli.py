import sys

import Adonis
from pyflags.flag import Flags

def cli() -> Flags | None:
    flag = Flags()
    flag.add(["--before", "-b"], "What is it now", str, required=True)
    flag.add(["--after", "-a"], "What would you like it to be", str, required=True)
    flag.add(["--cwd", "-c"], "What is the starting dir you want to walk through", str, default=".")
    flag.add(["--ignore", "-i"], "Any files or dirs to skip", list[str])
    flag.add(["--search", "-s"], "Just search for the string", bool)
    flag.add(["--dry-run", "-d"], "just print what you would change, don't actually change it", bool)

    flag.add(["--help", "-h"], "just print what you would change, don't actually change it", bool, default=False)
    flag.add(["--version", "-V"], "just print what you would change, don't actually change it", bool, default=False)
    flag.add(["--verbose", "-v"], "just print what you would change, don't actually change it", bool, default=True)
    flag.add(["--quiet", "-q"], "just print what you would change, don't actually change it", bool)

    if len(sys.argv) > 1:
        Adonis.PrintInfo("Parsing from command line arguments...")
        flag.parse_and_resolve(sys.argv[1:])

        if flag.help or flag.version:
            if flag.help:
                help_test = flag.help_text_ordered()
                assert isinstance(help_test, str)
                Adonis.PrintInfo(help_test)
            else:
                Adonis.PrintInfo("0.3.1")
            sys.exit(0)
        return flag
    else:
        # TODO: impliment
        """ Adonis.PrintInfo("Parsing from stdin...")
        sys.stdin """
        pass