# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
Test for linting over LSP.
"""

import sys
from threading import Event

import pytest
from hamcrest import assert_that, greater_than, is_

from .lsp_test_client import constants, defaults, session, utils

TEST_FILE_PATH = constants.TEST_DATA / "sample1" / "sample.py"
TEST_FILE_URI = utils.as_uri(str(TEST_FILE_PATH))

# TODO: Write your tool specific tests here.
def test_server_example():
    """Test to ensure linting on file open."""
    contents = TEST_FILE_PATH.read_text()

    actual = []
    with session.LspSession() as ls_session:
        ls_session.initialize()

    expected = []
    assert_that(actual, is_(expected))
