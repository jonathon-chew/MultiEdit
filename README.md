# MultiEdit

## Summary
`MultiEdit` is a small Python command-line project for walking a directory tree and replacing one string with another across matching files. I built it as a learning project to practice recursive file traversal, CLI flag handling, search-and-replace behavior, and lightweight error handling.

## What This Project Demonstrates
- Python CLI structure with a module entrypoint
- recursive directory walking with `os.walk()`
- replace-all text edits across files
- ignore lists for skipping files and directories
- search-only mode for locating matches without editing
- dry-run mode for previewing substitutions before writing
- required flag handling with the `pyflags` library

## Current Features
- requires `--before` and `--after` values for every run
- supports an optional `--cwd` root directory, defaulting to `.`
- supports an `--ignore` list of file or directory names to skip
- supports `--search` to report files that contain the target string
- supports `--dry-run` to preview replacements without writing changes
- supports `--help` and `--version` CLI responses
- replaces all occurrences of the target string in each file when running normally
- skips any file that raises an error while reading or writing instead of stopping the whole scan

## Behavior Notes
- **Default behavior:** when neither `--search` nor `--dry-run` is set, `MultiEdit` rewrites files in place.
- **Search precedence:** if `--search` is enabled, the script reports matches and does not write changes.
- **Dry-run output:** if `--dry-run` is enabled without `--search`, the script prints highlighted replacement lines instead of modifying files.
- **Ignore matching:** ignore checks are performed against the path segments returned by `os.path.split()`, so a file is skipped when any path component matches an ignored name.
- **Error handling:** unreadable files, permission issues, and other file-level exceptions are logged and then skipped.
- **Unused flags:** `--verbose` and `--quiet` are parsed by the CLI, but the current implementation does not use them yet.

## How To Run

The main entrypoint is the `src/MultiEdit/__main__.py` script:

```bash
python src/MultiEdit/__main__.py --before old_text --after new_text
```

You can also point it at a specific directory:

```bash
python src/MultiEdit/__main__.py --before old_text --after new_text --cwd ./notes
```

## Examples

### Replace Text In Place

```bash
python src/MultiEdit/__main__.py --before foo --after bar --cwd ./docs
```

This walks `./docs` and replaces every `foo` string it finds with `bar`.

### Preview Changes Without Writing

```bash
python src/MultiEdit/__main__.py --before foo --after bar --cwd ./docs --dry-run
```

This prints the lines that would change, but leaves the files untouched.

### Search Only

```bash
python src/MultiEdit/__main__.py --before foo --after bar --cwd ./docs --search
```

This reports which files contain `foo` and does not perform edits.

### Skip Paths

```bash
python src/MultiEdit/__main__.py --before foo --after bar --cwd ./docs --ignore .git --ignore build
```

This skips any file path that includes `.git` or `build` as a path component.

## Why This Is Different

Many simple replace tools either edit files blindly or stop at the first error. `MultiEdit` is deliberately lightweight, but it adds a few useful controls:
- a guided CLI built on `pyflags`
- search and preview modes before committing edits
- ignore support for common skip paths
- per-file error handling so one bad file does not cancel the whole run

That makes it handy for small batch edits, cleanup passes, and repetitive refactors where you want a quick command-line tool rather than a full editor workflow.

## Testing

This project includes a small test suite under `tests/`, along with a large set of sample text fixtures used for exercising the replacement logic.

The tests currently focus on:
- CLI flag parsing behavior
- replacement and search flow
- file traversal through nested test data
- ignore and dry-run handling
