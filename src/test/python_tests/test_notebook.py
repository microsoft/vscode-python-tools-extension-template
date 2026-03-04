# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
Tests for Jupyter notebook cell support over LSP.

These are template-style example tests that demonstrate how to validate notebook
cell diagnostics. Adapt the expected diagnostics to match your tool's output.
"""

import os
from threading import Event

from .lsp_test_client import constants, defaults, session, utils

TIMEOUT = 10  # seconds


def _make_notebook_uri(notebook_path: str) -> str:
    """Returns a 'file:' URI for a notebook path."""
    return utils.as_uri(notebook_path)


def _make_cell_uri(notebook_path: str, cell_id: str) -> str:
    """Returns a 'vscode-notebook-cell:' URI for a notebook cell.

    Args:
        notebook_path: Absolute path to the .ipynb file.
        cell_id: Fragment identifier for the cell (e.g. 'W0sZmlsZQ%3D%3D0').
    """
    nb_uri = utils.as_uri(notebook_path)
    # Replace 'file:' scheme with 'vscode-notebook-cell:'
    cell_uri = nb_uri.replace("file:", "vscode-notebook-cell:", 1)
    return f"{cell_uri}#{cell_id}"


def test_notebook_did_open():
    """Diagnostics are published for each code cell when a notebook is opened.

    This test sends a notebookDocument/didOpen notification for a notebook with
    one code cell and verifies that a publishDiagnostics notification is received
    for that cell's URI.

    TODO: Update the expected diagnostics to match your tool's output.
    """
    nb_path = str(constants.TEST_DATA / "sample1" / "sample.ipynb")
    nb_uri = _make_notebook_uri(nb_path)
    cell_id = "cell1"
    cell_uri = _make_cell_uri(nb_path, cell_id)
    cell_contents = "x = 1\n"

    with session.LspSession() as ls_session:
        ls_session.initialize(defaults.VSCODE_DEFAULT_INITIALIZE)

        done = Event()
        received = []

        def _handler(params):
            received.append(params)
            done.set()

        ls_session.set_notification_callback(session.PUBLISH_DIAGNOSTICS, _handler)

        ls_session.notify_notebook_did_open(
            {
                "notebookDocument": {
                    "uri": nb_uri,
                    "notebookType": "jupyter-notebook",
                    "version": 1,
                    "metadata": {},
                    "cells": [
                        {
                            "kind": 2,  # Code cell
                            "document": cell_uri,
                            "metadata": {},
                            "executionSummary": None,
                        }
                    ],
                },
                "cellTextDocuments": [
                    {
                        "uri": cell_uri,
                        "languageId": "python",
                        "version": 1,
                        "text": cell_contents,
                    }
                ],
            }
        )

        done.wait(TIMEOUT)

        # TODO: Add your tool-specific assertion on `received`.
        # For now, just verify we got a diagnostics notification for the cell.
        assert any(
            r.get("uri") == cell_uri for r in received
        ), f"Expected diagnostics for {cell_uri!r}, got: {received}"


def test_notebook_did_change_text_content():
    """Diagnostics update when the text content of a cell changes.

    TODO: Update the expected diagnostics to match your tool's output.
    """
    nb_path = str(constants.TEST_DATA / "sample1" / "sample.ipynb")
    nb_uri = _make_notebook_uri(nb_path)
    cell_id = "cell1"
    cell_uri = _make_cell_uri(nb_path, cell_id)
    initial_contents = "x = 1\n"
    updated_contents = "y = 2\n"

    with session.LspSession() as ls_session:
        ls_session.initialize(defaults.VSCODE_DEFAULT_INITIALIZE)

        # Open notebook first
        ls_session.notify_notebook_did_open(
            {
                "notebookDocument": {
                    "uri": nb_uri,
                    "notebookType": "jupyter-notebook",
                    "version": 1,
                    "metadata": {},
                    "cells": [
                        {
                            "kind": 2,
                            "document": cell_uri,
                            "metadata": {},
                            "executionSummary": None,
                        }
                    ],
                },
                "cellTextDocuments": [
                    {
                        "uri": cell_uri,
                        "languageId": "python",
                        "version": 1,
                        "text": initial_contents,
                    }
                ],
            }
        )

        done = Event()
        received = []

        def _handler(params):
            received.append(params)
            done.set()

        ls_session.set_notification_callback(session.PUBLISH_DIAGNOSTICS, _handler)

        # Send a change with updated text content
        ls_session.notify_notebook_did_change(
            {
                "notebookDocument": {
                    "uri": nb_uri,
                    "version": 2,
                },
                "change": {
                    "metadata": None,
                    "cells": {
                        "structure": None,
                        "data": None,
                        "textContent": [
                            {
                                "document": {"uri": cell_uri, "version": 2},
                                "changes": [
                                    {
                                        "text": updated_contents,
                                    }
                                ],
                            }
                        ],
                    },
                },
            }
        )

        done.wait(TIMEOUT)

        # TODO: Add your tool-specific assertion on `received`.
        assert any(
            r.get("uri") == cell_uri for r in received
        ), f"Expected diagnostics for {cell_uri!r}, got: {received}"


def test_notebook_did_save():
    """All code cells are re-linted when a notebook is saved.

    TODO: Update the expected diagnostics to match your tool's output.
    """
    nb_path = str(constants.TEST_DATA / "sample1" / "sample.ipynb")
    nb_uri = _make_notebook_uri(nb_path)
    cell_id = "cell1"
    cell_uri = _make_cell_uri(nb_path, cell_id)
    cell_contents = "x = 1\n"

    with session.LspSession() as ls_session:
        ls_session.initialize(defaults.VSCODE_DEFAULT_INITIALIZE)

        # Open notebook first
        ls_session.notify_notebook_did_open(
            {
                "notebookDocument": {
                    "uri": nb_uri,
                    "notebookType": "jupyter-notebook",
                    "version": 1,
                    "metadata": {},
                    "cells": [
                        {
                            "kind": 2,
                            "document": cell_uri,
                            "metadata": {},
                            "executionSummary": None,
                        }
                    ],
                },
                "cellTextDocuments": [
                    {
                        "uri": cell_uri,
                        "languageId": "python",
                        "version": 1,
                        "text": cell_contents,
                    }
                ],
            }
        )

        done = Event()
        received = []

        def _handler(params):
            received.append(params)
            done.set()

        ls_session.set_notification_callback(session.PUBLISH_DIAGNOSTICS, _handler)

        ls_session.notify_notebook_did_save(
            {
                "notebookDocument": {
                    "uri": nb_uri,
                    "version": 1,
                }
            }
        )

        done.wait(TIMEOUT)

        # TODO: Add your tool-specific assertion on `received`.
        assert any(
            r.get("uri") == cell_uri for r in received
        ), f"Expected diagnostics for {cell_uri!r}, got: {received}"


def test_notebook_did_change_new_cell_kind_filter():
    """Diagnostics are only published for newly added code cells, not markdown cells.

    When a notebook change adds both a code cell and a markdown cell via
    structure.did_open, only the code cell should receive diagnostics.
    """
    nb_path = str(constants.TEST_DATA / "sample1" / "sample.ipynb")
    nb_uri = _make_notebook_uri(nb_path)
    code_cell_id = "cell_code"
    md_cell_id = "cell_md"
    code_cell_uri = _make_cell_uri(nb_path, code_cell_id)
    md_cell_uri = _make_cell_uri(nb_path, md_cell_id)

    with session.LspSession() as ls_session:
        ls_session.initialize(defaults.VSCODE_DEFAULT_INITIALIZE)

        # Open an initially empty notebook
        ls_session.notify_notebook_did_open(
            {
                "notebookDocument": {
                    "uri": nb_uri,
                    "notebookType": "jupyter-notebook",
                    "version": 1,
                    "metadata": {},
                    "cells": [],
                },
                "cellTextDocuments": [],
            }
        )

        received = []
        done = Event()

        def _handler(params):
            received.append(params)
            done.set()

        ls_session.set_notification_callback(session.PUBLISH_DIAGNOSTICS, _handler)

        # Add both a code cell (kind=2) and a markdown cell (kind=1) at once
        ls_session.notify_notebook_did_change(
            {
                "notebookDocument": {
                    "uri": nb_uri,
                    "version": 2,
                },
                "change": {
                    "metadata": None,
                    "cells": {
                        "structure": {
                            "array": {
                                "start": 0,
                                "deleteCount": 0,
                                "cells": [
                                    {
                                        "kind": 2,  # Code
                                        "document": code_cell_uri,
                                        "metadata": {},
                                        "executionSummary": None,
                                    },
                                    {
                                        "kind": 1,  # Markdown
                                        "document": md_cell_uri,
                                        "metadata": {},
                                        "executionSummary": None,
                                    },
                                ],
                            },
                            "didOpen": [
                                {
                                    "uri": code_cell_uri,
                                    "languageId": "python",
                                    "version": 1,
                                    "text": "x = 1\n",
                                },
                                {
                                    "uri": md_cell_uri,
                                    "languageId": "markdown",
                                    "version": 1,
                                    "text": "# heading\n",
                                },
                            ],
                            "didClose": None,
                        },
                        "data": None,
                        "textContent": None,
                    },
                },
            }
        )

        done.wait(TIMEOUT)

        # The code cell should receive diagnostics; the markdown cell must not.
        uris_with_diagnostics = {r.get("uri") for r in received}
        assert code_cell_uri in uris_with_diagnostics, (
            f"Expected diagnostics for code cell {code_cell_uri!r}, got: {received}"
        )
        assert md_cell_uri not in uris_with_diagnostics, (
            f"Markdown cell {md_cell_uri!r} should not receive diagnostics, got: {received}"
        )


def test_notebook_did_close():
    """Diagnostics are cleared for all cells when a notebook is closed.

    TODO: Update the expected diagnostics to match your tool's output.
    """
    nb_path = str(constants.TEST_DATA / "sample1" / "sample.ipynb")
    nb_uri = _make_notebook_uri(nb_path)
    cell_id = "cell1"
    cell_uri = _make_cell_uri(nb_path, cell_id)
    cell_contents = "x = 1\n"

    with session.LspSession() as ls_session:
        ls_session.initialize(defaults.VSCODE_DEFAULT_INITIALIZE)

        # Open notebook first
        ls_session.notify_notebook_did_open(
            {
                "notebookDocument": {
                    "uri": nb_uri,
                    "notebookType": "jupyter-notebook",
                    "version": 1,
                    "metadata": {},
                    "cells": [
                        {
                            "kind": 2,
                            "document": cell_uri,
                            "metadata": {},
                            "executionSummary": None,
                        }
                    ],
                },
                "cellTextDocuments": [
                    {
                        "uri": cell_uri,
                        "languageId": "python",
                        "version": 1,
                        "text": cell_contents,
                    }
                ],
            }
        )

        done = Event()
        received = []

        def _handler(params):
            received.append(params)
            done.set()

        ls_session.set_notification_callback(session.PUBLISH_DIAGNOSTICS, _handler)

        ls_session.notify_notebook_did_close(
            {
                "notebookDocument": {
                    "uri": nb_uri,
                    "version": 1,
                },
                "cellTextDocuments": [
                    {"uri": cell_uri}
                ],
            }
        )

        done.wait(TIMEOUT)

        # Diagnostics should be cleared (empty list) for the cell URI
        assert any(
            r.get("uri") == cell_uri and r.get("diagnostics") == []
            for r in received
        ), f"Expected empty diagnostics for {cell_uri!r}, got: {received}"
