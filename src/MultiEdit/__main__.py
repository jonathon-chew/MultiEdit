import os, sys
import cli

import Adonis


def main():
    flags = cli.cli()
    assert flags is not None

    was = flags.before
    tobe = flags.after

    coloured_to_be = Adonis.ReturnBoldHighIntensity("purple",tobe)

    assert isinstance(was, str)
    assert isinstance(tobe, str)

    if not os.path.exists(flags.cwd):
        Adonis.PrintError(f"Directory {flags.cwd} does not exist")
        sys.exit(1)

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
                        Adonis.PrintInfo("Looking at: " + file + f" replacing {was} with {tobe}")
                        print(content)
                    elif flags.search:
                        if flags.before in r.read():
                            Adonis.PrintInfo("Is in: " + filepath) 
                    else:
                        contents = r.read()

            except Exception as e:
                Adonis.PrintInfo("Looking at: " + file + f" replacing {was} with {tobe}")
                Adonis.PrintError(f"[ERROR]: {e}")
                continue
            
            if not flags.dry_run and not flags.search:
                with open(filepath, "w") as w:
                    w.write(contents.replace(was, tobe, count=-1))
                    Adonis.PrintInfo("Updated: " + file + f" replacing {was} with {tobe}")

if __name__ == "__main__":
    main()