# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Pytest configuration: mock bundled LSP dependencies so lsp_server can be imported."""
import sys
import types
import pathlib


def _make_lsp_types_module():
    """Return a mock lsprotocol.types module with all attributes used by lsp_server."""
    mod = types.ModuleType("lsprotocol.types")

    # String constants used as feature identifiers.
    for name in [
        "TEXT_DOCUMENT_DID_OPEN",
        "TEXT_DOCUMENT_DID_SAVE",
        "TEXT_DOCUMENT_DID_CLOSE",
        "TEXT_DOCUMENT_FORMATTING",
        "INITIALIZE",
        "EXIT",
        "SHUTDOWN",
    ]:
        setattr(mod, name, name)

    # Stub types – only construction/access is needed, not real behaviour.
    for name in [
        "Diagnostic",
        "DiagnosticSeverity",
        "DidCloseTextDocumentParams",
        "DidOpenTextDocumentParams",
        "DidSaveTextDocumentParams",
        "DocumentFormattingParams",
        "InitializeParams",
        "Position",
        "Range",
        "TextEdit",
    ]:
        setattr(mod, name, type(name, (), {}))

    # MessageType enum-like object.
    msg_type = type("MessageType", (), {"Log": 4, "Error": 1, "Warning": 2, "Info": 3})
    mod.MessageType = msg_type

    return mod


class _MockLanguageServer:
    def __init__(self, **kwargs):
        pass

    def feature(self, *args, **kwargs):
        def decorator(func):
            return func

        return decorator

    def command(self, *args, **kwargs):
        def decorator(func):
            return func

        return decorator

    def show_message_log(self, *args, **kwargs):
        pass

    def show_message(self, *args, **kwargs):
        pass


def _install_mocks():
    mock_pygls = types.ModuleType("pygls")

    mock_server = types.ModuleType("pygls.server")
    mock_server.LanguageServer = _MockLanguageServer

    mock_workspace = types.ModuleType("pygls.workspace")
    mock_workspace.Document = type("Document", (), {"path": None})

    mock_uris = types.ModuleType("pygls.uris")
    mock_uris.from_fs_path = lambda p: "file://" + p

    mock_lsprotocol = types.ModuleType("lsprotocol")
    mock_lsp_types = _make_lsp_types_module()

    mock_jsonrpc = types.ModuleType("lsp_jsonrpc")
    mock_jsonrpc.shutdown_json_rpc = lambda: None

    mock_utils = types.ModuleType("lsp_utils")

    for name, mod in [
        ("pygls", mock_pygls),
        ("pygls.server", mock_server),
        ("pygls.workspace", mock_workspace),
        ("pygls.uris", mock_uris),
        ("lsprotocol", mock_lsprotocol),
        ("lsprotocol.types", mock_lsp_types),
        ("lsp_jsonrpc", mock_jsonrpc),
        ("lsp_utils", mock_utils),
    ]:
        if name not in sys.modules:
            sys.modules[name] = mod

    tool_dir = str(pathlib.Path(__file__).parents[3] / "bundled" / "tool")
    if tool_dir not in sys.path:
        sys.path.insert(0, tool_dir)


_install_mocks()
