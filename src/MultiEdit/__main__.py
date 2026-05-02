import os, sys
import Adonis
import cli

flags = cli.cli()
assert flags is not None

was = flags.before
tobe = flags.after
result = []

assert isinstance(was, str)
assert isinstance(tobe, str)

Adonis.PrintColour("blue", flags.debug_flags())

if not os.path.exists(flags.cwd):
    Adonis.PrintError(f"Directory {flags.cwd} does not exist")
    sys.exit(1)

for root, dirs, files in os.walk(flags.cwd):

    # Adonis.PrintInfo("Looking at: " + " " + root + " " + ', '.join(dirs) + " " + ', '.join(files))

    for file in files:
        filepath = os.path.join(root, file)

        if len(flags.ignore) > 0 and filepath in flags.ignore:
            Adonis.PrintWarning("ignoring " + file)
            continue

        Adonis.PrintInfo("Looking at " + filepath, end="\r")

        if not flags.dry_run and not flags.search:
            try:
                with open(filepath, "r") as r:
                    contents = r.read()
                with open(filepath, "w") as w:
                    w.write(contents.replace(was, tobe, count=-1))
            except Exception as e:
                Adonis.PrintError(str(e), end="\n")
                continue

        elif flags.search:
            try:
                with open(filepath, "r") as r:
                    if flags.before in r.read():
                        Adonis.PrintInfo("Is in: " + filepath)
            except Exception as e:
                Adonis.PrintError(str(e), end="\n")
                continue

        else:
            try:
                with open(filepath, "r") as r:
                    result = [Adonis.ReturnBoldHighIntensity("purple", line.replace(was, tobe, count=-1)) for line in r.readlines() if was in line]
            except Exception as e:
                Adonis.PrintError(str(e), end="\n")
                continue

if len(result) > 0:
    print('\n'.join(result))