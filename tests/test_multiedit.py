import importlib.util
import io
import sys
import types
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src" / "MultiEdit"
CLI_PATH = SRC_DIR / "cli.py"
MAIN_PATH = SRC_DIR / "__main__.py"


def _is_list_type(value_type):
    return value_type is list or getattr(value_type, "__origin__", None) is list


def _is_bool_type(value_type):
    return value_type is bool


def _coerce_value(value_type, raw_value):
    if value_type is str:
        return raw_value
    if value_type is int:
        return int(raw_value)
    if value_type is float:
        return float(raw_value)
    return raw_value


class FakeFlags:
    def __init__(self):
        self._definitions = []
        self._by_name = {}
        self.required_flags = set()
        self.helpers = {}
        self.help = False
        self.version = False
        self.verbose = False
        self.quiet = False

    def add(self, names, helper, value_type, required=False, default=None):
        canonical_name = names[0]
        attr_name = canonical_name.lstrip("-").replace("-", "_")
        is_list = _is_list_type(value_type)
        is_bool = _is_bool_type(value_type)

        if default is None:
            if is_list:
                default = []
            elif is_bool:
                default = False

        setattr(self, attr_name, default)

        record = {
            "names": list(names),
            "canonical_name": canonical_name,
            "attr_name": attr_name,
            "value_type": value_type,
            "is_list": is_list,
            "is_bool": is_bool,
            "required": required,
        }
        self._definitions.append(record)

        for name in names:
            self._by_name[name] = record
            self.helpers[name] = helper

        if required:
            self.required_flags.add(canonical_name)

    def parse_and_resolve(self, argv):
        index = 0
        while index < len(argv):
            token = argv[index]
            if not token.startswith("-"):
                index += 1
                continue

            name = token
            explicit_value = None
            if "=" in token:
                name, explicit_value = token.split("=", 1)

            record = self._by_name.get(name)
            if record is None:
                index += 1
                continue

            if record["is_bool"]:
                if explicit_value is None and index + 1 < len(argv):
                    next_value = argv[index + 1]
                    if not next_value.startswith("-") and next_value.lower() in {
                        "true",
                        "false",
                        "1",
                        "0",
                        "yes",
                        "no",
                        "on",
                        "off",
                    }:
                        explicit_value = next_value
                        index += 1

                if explicit_value is None:
                    value = True
                else:
                    value = explicit_value.lower() in {"true", "1", "yes", "on"}
                setattr(self, record["attr_name"], value)
            elif record["is_list"]:
                collected = []
                if explicit_value is not None:
                    collected.append(explicit_value)

                lookahead = index + 1
                while lookahead < len(argv) and not argv[lookahead].startswith("-"):
                    collected.append(argv[lookahead])
                    lookahead += 1

                current = getattr(self, record["attr_name"], [])
                setattr(self, record["attr_name"], list(current) + collected)
                index = lookahead - 1
            else:
                if explicit_value is None:
                    if index + 1 >= len(argv):
                        raise ValueError(f"Missing value for {name}")
                    explicit_value = argv[index + 1]
                    index += 1
                setattr(
                    self,
                    record["attr_name"],
                    _coerce_value(record["value_type"], explicit_value),
                )

            index += 1

        return self

    def help_text_ordered(self):
        lines = []
        for record in self._definitions:
            lines.append(
                f"{record['canonical_name']}: {self.helpers[record['canonical_name']]}"
            )
        return "\n".join(lines)


class FakeAdonis(types.ModuleType):
    def __init__(self):
        super().__init__("Adonis")
        self.info_messages = []
        self.error_messages = []

    def PrintInfo(self, message, end="\n"):
        self.info_messages.append((message, end))
        print(message, end=end)

    def PrintError(self, message, end="\n"):
        self.error_messages.append((message, end))
        print(message, end=end)

    def ReturnBoldHighIntensity(self, color, text):
        return f"<{color}>{text}</{color}>"


def install_stub_modules():
    fake_adonis = FakeAdonis()

    pyflags_pkg = types.ModuleType("pyflags")
    pyflags_flag = types.ModuleType("pyflags.flag")
    pyflags_flag.Flags = FakeFlags
    pyflags_pkg.flag = pyflags_flag

    sys.modules["Adonis"] = fake_adonis
    sys.modules["pyflags"] = pyflags_pkg
    sys.modules["pyflags.flag"] = pyflags_flag

    return fake_adonis


def load_module_from_path(module_name, module_path):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class MultiEditTestCase(unittest.TestCase):
    def setUp(self):
        self._original_argv = sys.argv[:]
        self._installed_modules = {}
        self.fake_adonis = install_stub_modules()
        self.cli_module = load_module_from_path("cli", CLI_PATH)
        self._installed_modules["cli"] = self.cli_module

    def tearDown(self):
        sys.argv = self._original_argv
        for name in ["cli", "Adonis", "pyflags.flag", "pyflags"]:
            sys.modules.pop(name, None)

    def load_main(self):
        module_name = f"multiedit_main_{self._testMethodName}"
        return load_module_from_path(module_name, MAIN_PATH)


class TestCli(MultiEditTestCase):
    def test_cli_parses_core_flags(self):
        sys.argv = [
            "MultiEdit",
            "--before",
            "foo",
            "--after",
            "bar",
            "--cwd",
            "./notes",
            "--ignore",
            ".git",
            "build",
            "--dry-run",
        ]

        flags = self.cli_module.cli()

        self.assertIsNotNone(flags)
        self.assertEqual(flags.before, "foo")
        self.assertEqual(flags.after, "bar")
        self.assertEqual(flags.cwd, "./notes")
        self.assertEqual(flags.ignore, [".git", "build"])
        self.assertTrue(flags.dry_run)
        self.assertFalse(flags.search)

    def test_cli_help_prints_help_and_exits(self):
        sys.argv = [
            "MultiEdit",
            "--before",
            "foo",
            "--after",
            "bar",
            "--help",
        ]

        with self.assertRaises(SystemExit) as exc:
            self.cli_module.cli()

        self.assertEqual(exc.exception.code, 0)
        self.assertTrue(any("What is it now" in msg for msg, _ in self.fake_adonis.info_messages))

    def test_cli_version_prints_version_and_exits(self):
        sys.argv = [
            "MultiEdit",
            "--before",
            "foo",
            "--after",
            "bar",
            "--version",
        ]

        with self.assertRaises(SystemExit) as exc:
            self.cli_module.cli()

        self.assertEqual(exc.exception.code, 0)
        self.assertTrue(any(msg == "0.3.1" for msg, _ in self.fake_adonis.info_messages))


class TestMainBehavior(MultiEditTestCase):
    def test_missing_cwd_exits_with_error(self):
        with TemporaryDirectory() as temp_dir:
            missing_dir = Path(temp_dir) / "does-not-exist"
            sys.argv = [
                "MultiEdit",
                "--before",
                "foo",
                "--after",
                "bar",
                "--cwd",
                str(missing_dir),
            ]

            with self.assertRaises(SystemExit) as exc:
                self.load_main()

        self.assertEqual(exc.exception.code, 1)
        self.assertTrue(
            any(
                f"Directory {missing_dir} does not exist" == msg
                for msg, _ in self.fake_adonis.error_messages
            )
        )

    def test_replaces_text_in_place(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            target = root / "notes.txt"
            target.write_text("foo keeps showing up\nanother foo line\n", encoding="utf-8")

            sys.argv = [
                "MultiEdit",
                "--before",
                "foo",
                "--after",
                "bar",
                "--cwd",
                str(root),
            ]

            with redirect_stdout(io.StringIO()):
                self.load_main()

            self.assertEqual(
                target.read_text(encoding="utf-8"),
                "bar keeps showing up\nanother bar line\n",
            )

    def test_search_mode_reports_matches_without_writing(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            target = root / "search.txt"
            target.write_text("foo is present here\n", encoding="utf-8")

            sys.argv = [
                "MultiEdit",
                "--before",
                "foo",
                "--after",
                "bar",
                "--cwd",
                str(root),
                "--search",
            ]

            with redirect_stdout(io.StringIO()):
                self.load_main()

            self.assertEqual(target.read_text(encoding="utf-8"), "foo is present here\n")
            self.assertTrue(
                any(msg == f"Is in: {target}" for msg, _ in self.fake_adonis.info_messages)
            )

    def test_dry_run_prints_preview_without_writing(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            target = root / "preview.txt"
            target.write_text("foo on the first line\n", encoding="utf-8")

            sys.argv = [
                "MultiEdit",
                "--before",
                "foo",
                "--after",
                "bar",
                "--cwd",
                str(root),
                "--dry-run",
            ]

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                self.load_main()

            self.assertEqual(target.read_text(encoding="utf-8"), "foo on the first line\n")
            output = buffer.getvalue()
            self.assertIn("<purple>bar on the first line\n</purple>", output)

    def test_ignore_list_skips_matching_paths(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            ignored_dir = root / ".git"
            ignored_dir.mkdir()
            ignored_file = ignored_dir / "config.txt"
            ignored_file.write_text("foo in ignored path\n", encoding="utf-8")

            active_file = root / "active.txt"
            active_file.write_text("foo in active path\n", encoding="utf-8")

            sys.argv = [
                "MultiEdit",
                "--before",
                "foo",
                "--after",
                "bar",
                "--cwd",
                str(root),
                "--ignore",
                ".git",
            ]

            with redirect_stdout(io.StringIO()):
                self.load_main()

            self.assertEqual(ignored_file.read_text(encoding="utf-8"), "foo in ignored path\n")
            self.assertEqual(active_file.read_text(encoding="utf-8"), "bar in active path\n")


if __name__ == "__main__":
    unittest.main()
