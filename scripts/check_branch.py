#!/usr/bin/env python
import sys
import re
import subprocess


def get_current_branch():
    return (
        subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        .decode("utf-8")
        .strip()
    )


def check_branch_name():
    branch = get_current_branch()

    # Protected branches
    protected = ["main", "master", "develop", "staging"]
    if branch in protected:
        print(f"❌ Cannot commit directly to {branch}")
        return 1

    # Branch pattern: type/GH-number-description
    pattern = r"^(feature|bugfix|test|docs|refactor)/GH-\d+-[a-z0-9-]+$"
    if not re.match(pattern, branch):
        print("❌ Branch name must match pattern: type/GH-number-description")
        print("Example: feature/GH-123-gmail-connectivity")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(check_branch_name())
