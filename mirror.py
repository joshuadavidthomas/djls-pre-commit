from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import urllib.request
from pathlib import Path

from packaging.version import Version

PROJECT = "django-language-server"
PYPI_URL = f"https://pypi.org/pypi/{PROJECT}/json"
DEPENDENCY = re.compile(r'("django-language-server==)([^"]+)(")')
README_REVISION = re.compile(r"(rev: v)([^\s]+)")


def released_versions() -> dict[Version, str]:
    with urllib.request.urlopen(PYPI_URL) as response:
        releases = json.load(response)["releases"]

    versions = {}
    for raw_version, files in releases.items():
        if files and not all(file.get("yanked", False) for file in files):
            versions[Version(raw_version)] = raw_version
    return versions


def replace_once(
    path: Path,
    pattern: re.Pattern[str],
    replacement: str,
) -> None:
    source = path.read_text()
    updated, count = pattern.subn(replacement, source)
    if count != 1:
        raise RuntimeError(f"expected one version in {path}, found {count}")
    path.write_text(updated)


def current_version() -> Version:
    match = DEPENDENCY.search(Path("pyproject.toml").read_text())
    if match is None:
        raise RuntimeError(
            "pyproject.toml must contain one exact django-language-server pin"
        )
    return Version(match.group(2))


def mirror(version: str) -> str:
    replace_once(
        Path("pyproject.toml"),
        DEPENDENCY,
        rf"\g<1>{version}\g<3>",
    )
    replace_once(
        Path("README.md"),
        README_REVISION,
        rf"\g<1>{version}",
    )
    subprocess.run(["git", "add", "pyproject.toml", "README.md"], check=True)
    subprocess.run(
        ["git", "commit", "-m", f"Mirror django-language-server {version}"],
        check=True,
    )
    tag = f"v{version}"
    subprocess.run(["git", "tag", tag], check=True)
    return tag


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", default=os.environ.get("DJLS_VERSION"))
    parser.add_argument("--github-output", type=Path)
    args = parser.parse_args()

    current = current_version()
    releases = released_versions()
    if args.version:
        requested = Version(args.version)
        if requested not in releases:
            raise RuntimeError(f"django-language-server {args.version} is not on PyPI")
        pending = [] if requested <= current else [requested]
    else:
        pending = sorted(version for version in releases if version > current)

    tags = [mirror(releases[version]) for version in pending]
    if args.github_output:
        with args.github_output.open("a") as output:
            output.write(f"tags={' '.join(tags)}\n")
    else:
        print(" ".join(tags))


if __name__ == "__main__":
    main()
