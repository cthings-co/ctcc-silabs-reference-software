#!/usr/bin/env python3
# Copyright (c) 2026 CTHINGS.CO
# SPDX-License-Identifier: Apache-2.0

"""Check DCO sign-offs for commits introduced by a pull request."""

import os
import subprocess
import sys


def git(*args, input_text=None):
    result = subprocess.run(
        ["git", *args],
        input=input_text,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout


def main():
    base = os.environ.get("DCO_BASE", "origin/main")
    head = os.environ.get("DCO_HEAD", "HEAD")

    commits = git("rev-list", "--reverse", f"{base}..{head}").splitlines()

    if not commits:
        print("ERROR: No commits found to check.")
        return 1

    failures = 0

    for commit in commits:
        author = git(
            "show", "-s", "--format=%an <%ae>", commit
        ).strip()

        message = git("show", "-s", "--format=%B", commit)

        trailers = git(
            "interpret-trailers",
            "--parse",
            "--no-divider",
            input_text=message,
        )

        signoffs = [
            line.partition(":")[2].strip()
            for line in trailers.splitlines()
            if line.lower().startswith("signed-off-by:")
        ]

        if author in signoffs:
            print(f"PASS: {commit[:8]} - {author}")
        else:
            print(f"FAIL: {commit[:8]} - {author}")
            print(f"  Expected: Signed-off-by: {author}")
            failures += 1

    if failures:
        print(f"\nDCO check failed: {failures} commit(s).")
        return 1

    print(f"\nDCO check passed: {len(commits)} commit(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
