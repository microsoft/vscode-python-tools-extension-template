// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

import { ConfigurationChangeEvent, WorkspaceFolder } from 'vscode';
import { getInterpreterDetails } from './python';
import { LoggingLevelSettingType } from './log/types';
import { getConfiguration, getWorkspaceFolders } from './vscodeapi';

export interface ISettings {
    workspace: string;
    logLevel: LoggingLevelSettingType;
    args: string[];
    path: string[];
    interpreter: string[];
}

export async function getExtensionSettings(namespace: string, includeInterpreter?: boolean): Promise<ISettings[]> {
    const settings: ISettings[] = [];
    const workspaces = getWorkspaceFolders();

    for (const workspace of workspaces) {
        const workspaceSetting = await getWorkspaceSettings(workspace, namespace, includeInterpreter);
        settings.push(workspaceSetting);
    }

    return settings;
}

export async function getWorkspaceSettings(
    workspace: WorkspaceFolder,
    namespace: string,
    includeInterpreter?: boolean,
): Promise<ISettings> {
    const config = getConfiguration(namespace, workspace.uri);
    const interpreter = includeInterpreter ? (await getInterpreterDetails(workspace.uri)).path : [];
    const workspaceSetting = {
        workspace: workspace.uri.toString(),
        logLevel: config.get<LoggingLevelSettingType>(`logLevel`) ?? 'error',
        args: config.get<string[]>(`args`) ?? [],
        path: config.get<string[]>(`path`) ?? [],
        interpreter: interpreter ?? [],
    };
    return workspaceSetting;
}

export function checkIfConfigurationChanged(e: ConfigurationChangeEvent, namespace: string): boolean {
    const settings = [`${namespace}.trace`, `${namespace}.args`, `${namespace}.path`];
    const changed = settings.map((s) => e.affectsConfiguration(s));
    return changed.includes(true);
}
