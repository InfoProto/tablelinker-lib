import io
import os
import re
import sys

import pytest

from tablelinker import Table

sample_dir = os.path.join(os.path.dirname(__file__), "../sample/")


def test_excel():
    table = Table(os.path.join(sample_dir, "hachijo_sightseeing.xlsx"))

    import pdb
    pdb.set_trace()
