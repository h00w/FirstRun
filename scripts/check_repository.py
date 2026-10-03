"""Check local links in tracked Markdown without third-party dependencies."""

from pathlib import Path
import re
import subprocess
from urllib.parse import unquote, urlsplit


LINK = re.compile(r"!?\[[^\]]*\]\(([^)]*)\)")
DEFINITION = re.compile(r"^ {0,3}\[([^\]]+)\]:\s*(<[^>]*>|\S+).*$", re.MULTILINE)
REFERENCE = re.compile(r"!?\[([^\]]+)\]\[([^\]]*)\]")


def destination(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("<"):
        return raw[1:].partition(">")[0]
    return raw.split()[0] if raw else ""


def label(raw: str) -> str:
    return " ".join(raw.split()).casefold()


def broken_links(root: Path, files: list[Path]) -> list[str]:
    root = root.resolve()
    errors = []
    for file in files:
        text = file.read_text(encoding="utf-8")
        text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        definitions = {label(match.group(1)): destination(match.group(2))
                       for match in DEFINITION.finditer(text)}
        text = DEFINITION.sub("", text)
        targets = []
        for match in LINK.finditer(text):
            targets.append(destination(match.group(1)))
        text = LINK.sub("", text)
        for match in REFERENCE.finditer(text):
            reference = label(match.group(2) or match.group(1))
            if reference in definitions:
                targets.append(definitions[reference])
        text = REFERENCE.sub("", text)
        for match in re.finditer(r"!?\[([^\]]+)\]", text):
            reference = label(match.group(1))
            if reference in definitions:
                targets.append(definitions[reference])
        for target in targets:
            url = urlsplit(target)
            if url.scheme or url.netloc or not url.path:
                continue
            path = unquote(url.path)
            candidate = (root / path.lstrip("/") if path.startswith("/")
                         else file.parent / path).resolve()
            if not candidate.is_relative_to(root) or not candidate.exists():
                errors.append(f"{file.relative_to(root)}: broken local link {target}")
    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    tracked = subprocess.check_output(["git", "ls-files", "--cached", "--others",
                                       "--exclude-standard", "-z"], cwd=root).decode().split("\0")
    files = [root / path for path in tracked if path.endswith(".md")]
    errors = broken_links(root, files)
    for error in errors:
        print(error)
    print(f"Checked {len(files)} Markdown files; {len(errors)} broken local links.")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
