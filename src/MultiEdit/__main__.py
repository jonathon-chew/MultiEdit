import os, sys
import cli

import Adonis

flags = cli.cli()
assert flags is not None

was = flags.before
tobe = flags.after
result = []

assert isinstance(was, str)
assert isinstance(tobe, str)

if not os.path.exists(flags.cwd):
    Adonis.PrintError(f"Directory {flags.cwd} does not exist")
    sys.exit(1)

for root, dirs, files in os.walk(flags.cwd):
    for file in files:
        filepath: str = os.path.join(root, file)
        split_file_path = filepath.split(os.sep)

        if any( ignore_file in flags.ignore for ignore_file in split_file_path):
            continue

        Adonis.PrintInfo("Looking at: " + file + f" replacing {was} with {tobe}")
        
        if not flags.dry_run and not flags.search:
            try:
                with open(filepath, "r") as r:
                    contents = r.read()
                with open(filepath, "w") as w:
                    w.write(contents.replace(was, tobe, count=-1))
            except Exception as e:
                Adonis.PrintError(filepath + " not dry run not search" + str(e), end="\n")
                continue

        elif flags.search:
            try:
                with open(filepath, "r") as r:
                    if flags.before in r.read():
                        Adonis.PrintInfo("Is in: " + filepath) 
            except Exception as e:
                Adonis.PrintError(filepath + " search error" + str(e), end="\n")
                continue

        else:
            try:
                with open(filepath, "r") as r:
                    result.append(''.join(Adonis.ReturnBoldHighIntensity("purple", line.replace(was, tobe, count=-1)) for line in r.readlines() if was in line))
            except Exception as e:
                Adonis.PrintError(filepath + " anything else error " + str(e), end="\n")
                continue

if result and len(result) > 0:
    print('\n'.join(result))