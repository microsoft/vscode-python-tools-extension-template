# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
Runner to use when running under a different interpreter.
"""

import os
import pathlib
import sys
import traceback

# Ensure that we can import LSP libraries, and other bundled libraries.
sys.path.append(os.fspath(pathlib.Path(__file__).parent.parent / "libs"))

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
                # TODO: `utils.run_module` is equivalent to running `python -m <pytool>`.
                # If your tool supports a programmatic API then replace the function below
                # with code for your tool. Also update `_run_tool_on_document` function and
                # `_run_tool` in `server.py`.
                result = utils.run_module(
                    module=msg["module"],
                    argv=msg["argv"],
                    use_stdin=msg["useStdin"],
                    cwd=msg["cwd"],
                    source=msg["source"] if "source" in msg else None,
                )
            except Exception as ex:  # pylint: disable=broad-except
                result = utils.RunResult("", traceback.format_exc())

        response = {"id": msg["id"]}
        if result.stderr:
            response["error"] = result.stderr

        if result.stdout:
            response["result"] = result.stdout

        RPC.send_data(response)
