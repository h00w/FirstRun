"""Check local links in tracked Markdown without third-party dependencies."""

from pathlib import Path
import re
import subprocess
from urllib.parse import unquote, urlsplit


LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


def broken_links(root: Path, files: list[Path]) -> list[str]:
    root = root.resolve()
    errors = []
    for file in files:
        text = file.read_text(encoding="utf-8")
        text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        for match in LINK.finditer(text):
            target = match.group(1).strip().split()[0].strip("<>")
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
