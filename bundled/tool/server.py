# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
Implementation of linting support over LSP.
"""

import json
import os
import pathlib
import sys
from typing import Any, Dict, List, Sequence, Union

# Ensure that we can import LSP libraries, and other bundled linter libraries
sys.path.append(str(pathlib.Path(__file__).parent.parent / "libs"))

# pylint: disable=wrong-import-position,import-error
import jsonrpc
import utils
from pygls import lsp, protocol, server, uris, workspace
from pygls.lsp import types


WORKSPACE_SETTINGS = {}
RUNNER = pathlib.Path(__file__).parent / "runner.py"

MAX_WORKERS = 5
LSP_SERVER = server.LanguageServer(max_workers=MAX_WORKERS)


# **********************************************************
# Tool specific code goes here
# **********************************************************

# Reference:
#  LS Protocol: https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/
#
#  Sample implementations:
#  Pylint: https://github.com/microsoft/vscode-pylint/blob/main/bundled/linter
#  Black: https://github.com/microsoft/vscode-black-formatter/blob/main/bundled/formatter

# TODO: Update this part as needed for your tool

@LSP_SERVER.feature(lsp.TEXT_DOCUMENT_DID_OPEN)
def did_open(_server: server.LanguageServer, params: types.DidOpenTextDocumentParams):
    """LSP handler for textDocument/didOpen request."""
    pass


@LSP_SERVER.feature(lsp.TEXT_DOCUMENT_DID_SAVE)
def did_save(_server: server.LanguageServer, params: types.DidSaveTextDocumentParams):
    """LSP handler for textDocument/didSave request."""
    pass


@LSP_SERVER.feature(lsp.TEXT_DOCUMENT_DID_CLOSE)
def did_close(_server: server.LanguageServer, params: types.DidCloseTextDocumentParams):
    """LSP handler for textDocument/didClose request."""
    # Publishing empty diagnostics to clear the entries for this file.
    text_document = LSP_SERVER.workspace.get_document(params.text_document.uri)
    LSP_SERVER.publish_diagnostics(text_document.uri, [])


@LSP_SERVER.feature(lsp.FORMATTING)
def formatting(_server: server.LanguageServer, params: types.DocumentFormattingParams):
    """LSP handler for textDocument/formatting request."""
    pass



# **********************************************************
# Required Language Server Initialization and Exit handlers
# **********************************************************
@LSP_SERVER.feature(lsp.INITIALIZE)
def initialize(params: types.InitializeParams):
    """LSP handler for initialize request."""
    LSP_SERVER.show_message_log(f"CWD Server: {os.getcwd()}")

    paths = "\r\n   ".join(sys.path)
    LSP_SERVER.show_message_log(f"sys.path used to run Server:\r\n   {paths}")

    settings = params.initialization_options["settings"]
    _update_workspace_settings(settings)
    LSP_SERVER.show_message_log(
        f"Settings used to run Server:\r\n{json.dumps(settings, indent=4, ensure_ascii=False)}\r\n"
    )

    if isinstance(LSP_SERVER.lsp, protocol.LanguageServerProtocol):
        trace = lsp.Trace.Off
        for setting in settings:
            if setting["trace"] == "debug":
                trace = lsp.Trace.Verbose
                break
            if setting["trace"] == "off":
                continue
            trace = lsp.Trace.Messages
        LSP_SERVER.lsp.trace = trace


@LSP_SERVER.feature(lsp.EXIT)
def on_exit():
    """Handle clean up on exit."""
    jsonrpc.shutdown_json_rpc()


# *****************************************************
# Internal settings management APIs
# *****************************************************
def _update_workspace_settings(settings):
    for setting in settings:
        key = uris.to_fs_path(setting["workspace"])
        WORKSPACE_SETTINGS[key] = {
            **setting,
            "workspaceFS": key,
        }


def _get_settings_by_document(document: workspace.Document):
    if len(WORKSPACE_SETTINGS) == 1 or document.path is None:
        return list(WORKSPACE_SETTINGS.values())[0]

    document_workspace = pathlib.Path(document.path)
    workspaces = [s["workspaceFS"] for s in WORKSPACE_SETTINGS.values()]

    while document_workspace != document_workspace.parent:
        if str(document_workspace) in workspaces:
            break
        document_workspace = document_workspace.parent

    return WORKSPACE_SETTINGS[str(document_workspace)]


if __name__ == "__main__":
    LSP_SERVER.start_io()
