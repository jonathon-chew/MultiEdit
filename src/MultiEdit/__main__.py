import os

import Adonis

import cli

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
    flags = cli.cli()
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
                        printer(f"Looking at: {file} replacing {was} with {tobe}", "info", flags.verbose)
                        if flags.verbose:
                            print(content)
                    elif flags.search:
                        if flags.before in r.read():
                            printer("Is in: " + filepath, "info", flags.verbose)
                    else:
                        contents = r.read()

            except Exception as e:
                printer("Looking at: " + file + f" replacing {was} with {tobe}", "info", flags.verbose)
                printer(f"[ERROR]: {e}", "error", flags.verbose)
                continue
            
            if not flags.dry_run and not flags.search:
                with open(filepath, "w") as w:
                    w.write(contents.replace(was, tobe, count=-1))
                    printer("Updated: " + file + f" replacing {was} with {tobe}", "info", flags.verbose)

if __name__ == "__main__":
    main()