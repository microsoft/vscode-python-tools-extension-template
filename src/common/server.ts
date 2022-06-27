// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

import { dirname } from 'path';
import { Disposable, OutputChannel, WorkspaceFolder } from 'vscode';
import { State } from 'vscode-languageclient';
import {
    LanguageClient,
    LanguageClientOptions,
    RevealOutputChannelOn,
    ServerOptions,
} from 'vscode-languageclient/node';
import { DEBUG_SERVER_SCRIPT_PATH, SERVER_SCRIPT_PATH } from './constants';
import { traceInfo, traceVerbose } from './log/logging';
import { getDebuggerPath } from './python';
import { getWorkspaceSettings, ISettings } from './settings';
import { traceLevelToLSTrace } from './utilities';
import { getWorkspaceFolders, isVirtualWorkspace } from './vscodeapi';

export type IInitOptions = { settings: ISettings[] };

function getProjectRoot(): WorkspaceFolder {
    const workspaces: readonly WorkspaceFolder[] = getWorkspaceFolders();
    if (workspaces.length === 1) {
        return workspaces[0];
    } else {
        let root = workspaces[0].uri.fsPath;
        let rootWorkspace = workspaces[0];
        for (const w of workspaces) {
            if (root.length > w.uri.fsPath.length) {
                root = w.uri.fsPath;
                rootWorkspace = w;
            }
        }
        return rootWorkspace;
    }
}

export async function createServer(
    interpreter: string[],
    serverId: string,
    serverName: string,
    outputChannel: OutputChannel,
    initializationOptions: IInitOptions,
): Promise<LanguageClient> {
    const command = interpreter[0];
    const cwd = getProjectRoot().uri.fsPath;

    // Set debugger path needed for debugging python code.
    const debugEnv = process.env;
    const debuggerPath = await getDebuggerPath();
    if (debugEnv.USE_DEBUGPY && debuggerPath) {
        debugEnv.DEBUGPY_PATH = debuggerPath;
    } else {
        debugEnv.USE_DEBUGPY = 'False';
    }

    const args =
        debugEnv.USE_DEBUGPY === 'False'
            ? interpreter.slice(1).concat([SERVER_SCRIPT_PATH])
            : interpreter.slice(1).concat([DEBUG_SERVER_SCRIPT_PATH]);
    traceInfo(`Server run command: ${[command, ...args].join(' ')}`);

    const serverOptions: ServerOptions = {
        command,
        args,
        options: { cwd, env: debugEnv },
    };

    // Options to control the language client
    const clientOptions: LanguageClientOptions = {
        // Register the server for python documents
        documentSelector: isVirtualWorkspace()
            ? [{ language: 'python' }]
            : [
                  { scheme: 'file', language: 'python' },
                  { scheme: 'untitled', language: 'python' },
                  { scheme: 'vscode-notebook', language: 'python' },
                  { scheme: 'vscode-notebook-cell', language: 'python' },
              ],
        outputChannel: outputChannel,
        traceOutputChannel: outputChannel,
        revealOutputChannelOn: RevealOutputChannelOn.Never,
        initializationOptions,
    };

    return new LanguageClient(serverId, serverName, serverOptions, clientOptions);
}

let _disposables: Disposable[] = [];
export async function restartServer(
    interpreter: string[],
    serverId: string,
    serverName: string,
    outputChannel: OutputChannel,
    initializationOptions: IInitOptions,
    lsClient?: LanguageClient,
): Promise<LanguageClient> {
    if (lsClient) {
        traceInfo(`Server: Stop requested`);
        await lsClient.stop();
        _disposables.forEach((d) => d.dispose());
        _disposables = [];
    }
    const newLSClient = await createServer(interpreter, serverId, serverName, outputChannel, initializationOptions);
    const workspaceSetting = await getWorkspaceSettings(getProjectRoot(), serverId);
    newLSClient.trace = traceLevelToLSTrace(workspaceSetting.logLevel);
    traceInfo(`Server: Start requested.`);
    _disposables.push(
        newLSClient.onDidChangeState((e) => {
            switch (e.newState) {
                case State.Stopped:
                    traceVerbose(`Server State: Stopped`);
                    break;
                case State.Starting:
                    traceVerbose(`Server State: Starting`);
                    break;
                case State.Running:
                    traceVerbose(`Server State: Running`);
                    break;
            }
        }),
        newLSClient.start(),
    );
    return newLSClient;
}
