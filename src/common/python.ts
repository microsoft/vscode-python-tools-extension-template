// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

/* eslint-disable @typescript-eslint/naming-convention */
import { commands, Disposable, Event, EventEmitter, extensions, Uri } from 'vscode';
import { traceError, traceLog } from './log/logging';
import { PythonExtension, ResolvedEnvironment } from '@vscode/python-extension';
import { PythonEnvironmentsAPI } from '../typings/pythonEnvironments';

export interface IInterpreterDetails {
    path?: string[];
    resource?: Uri;
}

const onDidChangePythonInterpreterEvent = new EventEmitter<IInterpreterDetails>();
export const onDidChangePythonInterpreter: Event<IInterpreterDetails> = onDidChangePythonInterpreterEvent.event;

let _api: PythonExtension | undefined;
async function getPythonExtensionAPI(): Promise<PythonExtension | undefined> {
    if (_api) {
        return _api;
    }
    _api = await PythonExtension.api();
    return _api;
}

const PYTHON_ENVIRONMENTS_EXTENSION_ID = 'ms-python.vscode-python-envs';

let _envsApi: PythonEnvironmentsAPI | undefined;
async function getEnvironmentsExtensionAPI(): Promise<PythonEnvironmentsAPI | undefined> {
    if (_envsApi) {
        return _envsApi;
    }
    const extension = extensions.getExtension(PYTHON_ENVIRONMENTS_EXTENSION_ID);
    if (!extension) {
        return undefined;
    }
    if (!extension.isActive) {
        await extension.activate();
    }
    _envsApi = extension.exports as PythonEnvironmentsAPI;
    return _envsApi;
}

export async function initializePython(disposables: Disposable[]): Promise<void> {
    try {
        const envsApi = await getEnvironmentsExtensionAPI();

        if (envsApi) {
            disposables.push(
                envsApi.onDidChangeEnvironment((e) => {
                    onDidChangePythonInterpreterEvent.fire({
                        path: e.new
                            ? [e.new.execInfo.run.executable]
                            : undefined,
                        resource: e.uri,
                    });
                }),
            );

            traceLog('Waiting for interpreter from python environments extension.');
            onDidChangePythonInterpreterEvent.fire(await getInterpreterDetails());
            return;
        }

        const api = await getPythonExtensionAPI();

        if (api) {
            disposables.push(
                api.environments.onDidChangeActiveEnvironmentPath((e) => {
                    onDidChangePythonInterpreterEvent.fire({ path: [e.path], resource: e.resource?.uri });
                }),
            );

            traceLog('Waiting for interpreter from python extension.');
            onDidChangePythonInterpreterEvent.fire(await getInterpreterDetails());
        }
    } catch (error) {
        traceError('Error initializing python: ', error);
    }
}

export async function resolveInterpreter(interpreter: string[]): Promise<ResolvedEnvironment | undefined> {
    const api = await getPythonExtensionAPI();
    return api?.environments.resolveEnvironment(interpreter[0]);
}

export async function getInterpreterDetails(resource?: Uri): Promise<IInterpreterDetails> {
    const envsApi = await getEnvironmentsExtensionAPI();
    if (envsApi) {
        const environment = await envsApi.getEnvironment(resource);
        if (environment) {
            return {
                path: [environment.execInfo.run.executable],
                resource,
            };
        }
        return { path: undefined, resource };
    }

    const api = await getPythonExtensionAPI();
    const environment = await api?.environments.resolveEnvironment(
        api?.environments.getActiveEnvironmentPath(resource),
    );
    if (environment?.executable.uri && checkVersion(environment)) {
        return { path: [environment?.executable.uri.fsPath], resource };
    }
    return { path: undefined, resource };
}

export async function getDebuggerPath(): Promise<string | undefined> {
    const api = await getPythonExtensionAPI();
    return api?.debug.getDebuggerPackagePath();
}

export async function runPythonExtensionCommand(command: string, ...rest: any[]) {
    await getPythonExtensionAPI();
    return await commands.executeCommand(command, ...rest);
}

export function checkVersion(resolved: ResolvedEnvironment | undefined): boolean {
    const version = resolved?.version;
    if (version?.major === 3 && version?.minor >= 8) {
        return true;
    }
    traceError(`Python version ${version?.major}.${version?.minor} is not supported.`);
    traceError(`Selected python path: ${resolved?.executable.uri?.fsPath}`);
    traceError('Supported versions are 3.8 and above.');
    return false;
}
