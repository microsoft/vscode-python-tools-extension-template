# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
Runner to use when running under a different interpreter.
"""

import os
import pathlib
import sys
import traceback

# Ensure that we can import LSP libraries, and other bundled linter libraries.
lib_path = os.fspath(pathlib.Path(__file__).parent.parent / "libs")
if lib_path not in sys.path and os.path.isdir(lib_path):
    sys.path.append(lib_path)
del lib_path

# pylint: disable=wrong-import-position,import-error
import jsonrpc
import utils

RPC = jsonrpc.create_json_rpc(sys.stdin.buffer, sys.stdout.buffer)

EXIT_NOW = False
while not EXIT_NOW:
    msg = RPC.receive_data()

    method = msg["method"]
    if method == "exit":
        EXIT_NOW = True
        continue

    if method == "run":
        # This is needed to preserve sys.path, pylint modifies
        # sys.path and that might not work for this scenario
        # next time around.
        with utils.substitute_attr(sys, "path", sys.path[:]):
            try:
                # TODO: `utils.run_module` is equivalent to running `python -m <pytool-module>`.
                # If your tool supports a programmatic API then replace the function below
                # with code for your tool. You can also use `utils.run_api` helper, which
                # handles changing working directories, managing io streams, etc.
                # Also update `_run_tool_on_document` and `_run_tool` functions in `server.py`.
                result = utils.run_module(
                    module=msg["module"],
                    argv=msg["argv"],
                    use_stdin=msg["useStdin"],
                    cwd=msg["cwd"],
                    source=msg["source"] if "source" in msg else None,
                )
            except Exception:  # pylint: disable=broad-except
                result = utils.RunResult("", traceback.format_exc())

        response = {"id": msg["id"]}
        if result.stderr:
            response["error"] = result.stderr
        elif result.stdout:
            response["result"] = result.stdout

        RPC.send_data(response)
