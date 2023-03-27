// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

import { ConfigurationChangeEvent, WorkspaceConfiguration, WorkspaceFolder } from 'vscode';
import { getInterpreterDetails } from './python';
import { getConfiguration, getWorkspaceFolders } from './vscodeapi';

export interface ISettings {
    cwd: string;
    workspace: string;
    args: string[];
    path: string[];
    interpreter: string[];
    importStrategy: string;
    showNotifications: string;
}

export async function getExtensionSettings(namespace: string, includeInterpreter?: boolean): Promise<ISettings[]> {
    const settings: ISettings[] = [];
    const workspaces = getWorkspaceFolders();

    for (const workspace of workspaces) {
        const workspaceSetting = await getWorkspaceSettings(namespace, workspace, includeInterpreter);
        settings.push(workspaceSetting);
    }

    return settings;
}

export function getInterpreterFromSetting(namespace: string) {
    const config = getConfiguration(namespace);
    return config.get<string[]>('interpreter');
}

export async function getWorkspaceSettings(
    namespace: string,
    workspace: WorkspaceFolder,
    includeInterpreter?: boolean,
): Promise<ISettings> {
    const config = getConfiguration(namespace, workspace.uri);

    let interpreter: string[] | undefined = [];
    if (includeInterpreter) {
        interpreter = getInterpreterFromSetting(namespace);
        if (interpreter === undefined || interpreter.length === 0) {
            interpreter = (await getInterpreterDetails(workspace.uri)).path;
        }
    }

    const workspaceSetting = {
        cwd: workspace.uri.fsPath,
        workspace: workspace.uri.toString(),
        args: config.get<string[]>(`args`) ?? [],
        path: config.get<string[]>(`path`) ?? [],
        interpreter: interpreter ?? [],
        importStrategy: config.get<string>(`importStrategy`) ?? 'fromEnvironment',
        showNotifications: config.get<string>(`showNotifications`) ?? 'off',
    };
    return workspaceSetting;
}

function getGlobalValue<T>(config: WorkspaceConfiguration, key: string, defaultValue: T): T {
    const inspect = config.inspect<T>(key);
    return inspect?.globalValue ?? inspect?.defaultValue ?? defaultValue;
}

export async function getGlobalSettings(namespace: string, includeInterpreter?: boolean): Promise<ISettings> {
    const config = getConfiguration(namespace);

    let interpreter: string[] | undefined = [];
    if (includeInterpreter) {
        interpreter = getGlobalValue<string[]>(config, 'interpreter', []);
        if (interpreter === undefined || interpreter.length === 0) {
            interpreter = (await getInterpreterDetails()).path;
        }
    }

    const setting = {
        cwd: process.cwd(),
        workspace: process.cwd(),
        args: getGlobalValue<string[]>(config, 'args', []),
        path: getGlobalValue<string[]>(config, 'path', []),
        interpreter: interpreter ?? [],
        importStrategy: getGlobalValue<string>(config, 'importStrategy', 'fromEnvironment'),
        showNotifications: getGlobalValue<string>(config, 'showNotifications', 'off'),
    };
    return setting;
}

export function checkIfConfigurationChanged(e: ConfigurationChangeEvent, namespace: string): boolean {
    const settings = [
        `${namespace}.args`,
        `${namespace}.path`,
        `${namespace}.interpreter`,
        `${namespace}.importStrategy`,
        `${namespace}.showNotifications`,
    ];
    const changed = settings.map((s) => e.affectsConfiguration(s));
    return changed.includes(true);
}
