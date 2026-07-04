import os
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

def printer(message: str, level: str, verbose: bool) -> None:
    if not verbose:
        return
    match level.lower():
        case "info":
            Adonis.PrintInfo(message)
        case "warning":
            Adonis.PrintWarning(message)
        case "error":
            Adonis.PrintError(message)
        case _:
            pass

def main():
    flags = cli()
    assert flags is not None

    was = flags.before
    tobe = flags.after

    coloured_to_be = Adonis.ReturnBoldHighIntensity("purple",tobe)

    assert isinstance(was, str)
    assert isinstance(tobe, str)

    if not os.path.exists(flags.cwd):
        printer(f"Directory {flags.cwd} does not exist", "error", flags.verbose)
        SystemExit(1)

    for root, _, files in os.walk(flags.cwd):
        for file in files:
            filepath: str = os.path.join(root, file)
            split_file_path = filepath.split(os.sep)

            if any( ignore_file in flags.ignore for ignore_file in split_file_path):
                continue

            contents = ""
            try:
                with open(filepath, "r") as r:
                    if flags.dry_run:
                        content = ''.join([line.replace(was, coloured_to_be, count=-1) for line in r.readlines() if was in line])
                        if not content:
                            continue
                        printer(f"Looking at: {filepath} replacing {was} with {tobe}", "info", flags.verbose)
                        if flags.verbose:
                            print(content)
                    elif flags.search:
                        if flags.before in r.read():
                            printer("Is in: " + filepath, "info", flags.verbose)
                    else:
                        contents = r.read()

            except Exception as e:
                if flags.show_errors:
                    printer("Looking at: " + filepath + f" replacing {was} with {tobe}", "info", flags.verbose)
                    printer(f"[ERROR]: {e}", "error", flags.verbose)
                continue
            
            if not flags.dry_run and not flags.search and flags.before in contents:
                with open(filepath, "w") as w:
                    w.write(contents.replace(was, tobe, count=-1))
                    printer("Updated: " + file + f" replacing {was} with {tobe}", "info", flags.verbose)

if __name__ == "__main__":
    main()
