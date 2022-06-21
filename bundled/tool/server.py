# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
Implementation of linting support over LSP.
"""

import copy
import json
import os
import pathlib
import sys
from typing import List, Optional, Sequence, Union

# Ensure that we can import LSP libraries, and other bundled linter libraries
sys.path.append(os.fspath(pathlib.Path(__file__).parent.parent / "libs"))

# Ensure debugger is loaded before we load anything else
if os.getenv("USE_DEBUGPY", None) in ["True", "TRUE", "1", "T"]:
    debugger_path = os.getenv("DEBUGPY_PATH", None)
    if debugger_path:
        if debugger_path.endswith("debugpy"):
            sys.path.append(os.fspath(pathlib.Path(debugger_path).parent))
        else:
            sys.path.append(debugger_path)

        import debugpy

        # 5678 is the default port, If you need to change it update it here
        # and in launch.json
        debugpy.connect(5678)

        # This will ensure that execution is paused as soon as the debugger
        # connects to VS Code. If you don't want to pause here comment this
        # line and set breakpoints as appropriate.
        debugpy.breakpoint()

        # TODO: Remove this block entirely to remove debugging support.
        # This was added for convenience to debug extension and python parts.
        # You can always debug using attach to process, even if you remove
        # this block of code.
        # NOTE: The above way of attaching debugger allows you to debug
        # any subprocess launched by this server. If you remove this code
        # you will have to manually attach to each process when debugging.

# **********************************************************
# Imports needed for the language server goes below this.
# **********************************************************
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
#  LS Protocol: https://microsoft.github.io/language-server-protocol/specifications/specification-3-16/
#
#  Sample implementations:
#  Pylint: https://github.com/microsoft/vscode-pylint/blob/main/bundled/linter
#  Black: https://github.com/microsoft/vscode-black-formatter/blob/main/bundled/formatter
#  isort: https://github.com/microsoft/vscode-isort/blob/main/bundled/formatter

# TODO: Update this part as needed for your tool
TOOL_MODULE = "<pytool>"
TOOL_ARGS = []  # default arguments always passed to your tool.


@LSP_SERVER.feature(lsp.TEXT_DOCUMENT_DID_OPEN)
def did_open(server: server.LanguageServer, params: types.DidOpenTextDocumentParams):
    """LSP handler for textDocument/didOpen request."""
    #  Sample implementations:
    #  Pylint: https://github.com/microsoft/vscode-pylint/blob/main/bundled/linter

    document = server.workspace.get_document(params.text_document.uri)
    # Use _run_tool_on_document function to run your tool on a document.
    # Use _run_tool function for general purpose running your tool.

    # Use this handler for linting on file Open. You have to publish an array of
    # lsp.Diagnostic objects with the each capturing a problem reported by linter
    # for that file.
    diagnostics: List[lsp.Diagnostic] = []

    # TODO: Use _run_tool_on_document to get the stdout from your tool, parse it here
    # and create instances of lsp.Diagnostic for each issue.

    LSP_SERVER.publish_diagnostics(document.uri, diagnostics)


@LSP_SERVER.feature(lsp.TEXT_DOCUMENT_DID_SAVE)
def did_save(_server: server.LanguageServer, params: types.DidSaveTextDocumentParams):
    """LSP handler for textDocument/didSave request."""
    #  Sample implementations:
    #  Pylint: https://github.com/microsoft/vscode-pylint/blob/main/bundled/linter

    document = server.workspace.get_document(params.text_document.uri)
    # Use _run_tool_on_document function to run your tool on a document.
    # Use _run_tool function for general purpose running your tool.

    # Use this handler for linting on file Save. You have to publish an array of
    # lsp.Diagnostic objects with the each capturing a problem reported by linter
    # for that file.
    diagnostics: List[lsp.Diagnostic] = []

    # TODO: Use _run_tool_on_document to get the stdout from your tool, parse it here
    # and create instances of lsp.Diagnostic for each issue.

    LSP_SERVER.publish_diagnostics(document.uri, diagnostics)


@LSP_SERVER.feature(lsp.TEXT_DOCUMENT_DID_CLOSE)
def did_close(_server: server.LanguageServer, params: types.DidCloseTextDocumentParams):
    """LSP handler for textDocument/didClose request."""
    document = LSP_SERVER.workspace.get_document(params.text_document.uri)
    # Publishing empty diagnostics to clear the entries for this file.
    LSP_SERVER.publish_diagnostics(document.uri, [])


@LSP_SERVER.feature(lsp.FORMATTING)
def formatting(_server: server.LanguageServer, params: types.DocumentFormattingParams):
    """LSP handler for textDocument/formatting request."""
    #  Sample implementations:
    #  Black: https://github.com/microsoft/vscode-black-formatter/blob/main/bundled/formatter

    # If your tool is a formatter you can use this handler to provide formatting support on save.
    # You have to return an array of lsp.TextEdit objects, to provide your formatted results.
    # If you provide [] array, VS Code will clear the file of all contents.

    # For no changes in formatting return None.
    return None


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


def _get_settings_by_document(document: Optional[workspace.Document]):
    if len(WORKSPACE_SETTINGS) == 1 or document is None or document.path is None:
        return list(WORKSPACE_SETTINGS.values())[0]

    document_workspace = pathlib.Path(document.path)
    workspaces = [s["workspaceFS"] for s in WORKSPACE_SETTINGS.values()]

    while document_workspace != document_workspace.parent:
        if str(document_workspace) in workspaces:
            break
        document_workspace = document_workspace.parent

    return WORKSPACE_SETTINGS[str(document_workspace)]


# *****************************************************
# Internal execution APIs
# *****************************************************
def _run_tool_on_document(
    document: workspace.Document,
    use_stdin: bool = False,
) -> Union[utils.RunResult, None]:
    """Runs tool on the given document.

    params:
      - use_stdin: bool = Default False. When True passes the contents of the documents to the
    """
    if str(document.uri).startswith("vscode-notebook-cell"):
        # TODO: Decide on if you want to skip notebook cells.
        # Skip notebook cells
        return None

    if utils.is_stdlib_file(document.path):
        # TODO: Decide on if you want to skip standard library files.
        # Skip standard library python files.
        return None

    # deep copy here to prevent accidentally updating global settings.
    settings = copy.deepcopy(_get_settings_by_document(document))

    code_workspace = settings["workspaceFS"]
    cwd = settings["workspaceFS"]

    use_path = False
    use_rpc = False
    if len(settings["path"]) > 0:
        # 'path' setting takes priority over everything.
        use_path = True
        argv = settings["path"]
    elif len(settings["interpreter"]) > 0 and not utils.is_current_interpreter(
        settings["interpreter"][0]
    ):
        # If there is a different interpreter set use JSON-RPC to the subprocess
        # running under that interpreter.
        argv = [TOOL_MODULE]
        use_rpc = True
    else:
        # if the interpreter is same as the interpreter running this
        # process then run as module.
        argv = [TOOL_MODULE]

    argv += TOOL_ARGS + settings["args"]

    if use_stdin:
        # TODO: update these to pass the appropriate arguments to provide document contents
        # to tool via stdin.
        # For example, for pylint args for stdin looks like this:
        #     pylint --from-stdin <path>
        # Here `--from-stdin` path is used by pylint to make decisions on the file contents
        # that are being processed. Like, applying exclusion rules.
        # It should look like this when you pass it:
        #     argv += ["--from-stdin", document.path]
        # Read up on how your tool handles contents via stdin. If stdin is not supported use
        # set use_stdin to False, or provide path, what ever is appropriate for your tool.
        argv += []

    if use_path:
        # This mode is used when running executables.
        LSP_SERVER.show_message_log(" ".join(argv))
        LSP_SERVER.show_message_log(f"CWD Server: {cwd}")
        result = utils.run_path(
            argv=argv,
            use_stdin=use_stdin,
            cwd=cwd,
            source=document.source.replace("\r\n", "\n"),
        )
    elif use_rpc:
        # This mode is used if the interpreter running this server is different from
        # the interpreter used for running this server.
        LSP_SERVER.show_message_log(" ".join(settings["interpreter"] + ["-m"] + argv))
        LSP_SERVER.show_message_log(f"CWD Linter: {cwd}")
        result = jsonrpc.run_over_json_rpc(
            workspace=code_workspace,
            interpreter=settings["interpreter"],
            module=TOOL_MODULE,
            argv=argv,
            use_stdin=use_stdin,
            cwd=cwd,
            source=document.source,
        )
    else:
        # In this mode the tool is run as a module in the same process as the language server.
        LSP_SERVER.show_message_log(" ".join([sys.executable, "-m"] + argv))
        LSP_SERVER.show_message_log(f"CWD Linter: {cwd}")
        # This is needed to preserve sys.path, in cases where the tool modifies
        # sys.path and that might not work for this scenario next time around.
        with utils.substitute_attr(sys, "path", sys.path[:]):
            result = utils.run_module(
                module=TOOL_MODULE,
                argv=argv,
                use_stdin=use_stdin,
                cwd=cwd,
                source=document.source,
            )

    if result.stderr:
        LSP_SERVER.show_message_log(result.stderr, msg_type=lsp.MessageType.Error)
    LSP_SERVER.show_message_log(f"{document.uri} :\r\n{result.stdout}")
    return result


def _run_tool(extra_args: Sequence[str]) -> utils.RunResult:
    """Runs tool."""
    # deep copy here to prevent accidentally updating global settings.
    settings = copy.deepcopy(_get_settings_by_document(None))

    code_workspace = settings["workspaceFS"]
    cwd = settings["workspaceFS"]

    use_path = False
    use_rpc = False
    if len(settings["path"]) > 0:
        # 'path' setting takes priority over everything.
        use_path = True
        argv = settings["path"]
    elif len(settings["interpreter"]) > 0 and not utils.is_current_interpreter(
        settings["interpreter"][0]
    ):
        # If there is a different interpreter set use JSON-RPC to the subprocess
        # running under that interpreter.
        argv = [TOOL_MODULE]
        use_rpc = True
    else:
        # if the interpreter is same as the interpreter running this
        # process then run as module.
        argv = [TOOL_MODULE]

    argv += extra_args

    if use_path:
        # This mode is used when running executables.
        LSP_SERVER.show_message_log(" ".join(argv))
        LSP_SERVER.show_message_log(f"CWD Server: {cwd}")
        result = utils.run_path(argv=argv, use_stdin=True, cwd=cwd)
    elif use_rpc:
        # This mode is used if the interpreter running this server is different from
        # the interpreter used for running this server.
        LSP_SERVER.show_message_log(" ".join(settings["interpreter"] + ["-m"] + argv))
        LSP_SERVER.show_message_log(f"CWD Linter: {cwd}")
        result = jsonrpc.run_over_json_rpc(
            workspace=code_workspace,
            interpreter=settings["interpreter"],
            module=TOOL_MODULE,
            argv=argv,
            use_stdin=True,
            cwd=cwd,
        )
    else:
        # In this mode the tool is run as a module in the same process as the language server.
        LSP_SERVER.show_message_log(" ".join([sys.executable, "-m"] + argv))
        LSP_SERVER.show_message_log(f"CWD Linter: {cwd}")
        # This is needed to preserve sys.path, in cases where the tool modifies
        # sys.path and that might not work for this scenario next time around.
        with utils.substitute_attr(sys, "path", sys.path[:]):
            result = utils.run_module(
                module=TOOL_MODULE, argv=argv, use_stdin=True, cwd=cwd
            )

    if result.stderr:
        LSP_SERVER.show_message_log(result.stderr, msg_type=lsp.MessageType.Error)
    LSP_SERVER.show_message_log(f"\r\n{result.stdout}\r\n")
    return result


if __name__ == "__main__":
    LSP_SERVER.start_io()
