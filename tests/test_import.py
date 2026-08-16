# -*- coding: utf-8 -*-
import os
import subprocess
import sys


sys.path.insert(0, os.path.abspath(".."))

from steem import *  # noqa
from steembase import *  # noqa


# pylint: disable=unused-import,unused-variable
def test_import():
    _ = Steem()
    _ = account.PasswordKey


def test_cli_help():
    result = subprocess.run(
        ["steempy", "-h"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "usage:" in result.stdout.lower()
