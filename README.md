# Template for VS Code python tools extensions

This is a template repository to get you started on building a VS Code extension for your favorite python tool. It code be a linter, formatter, or code analysis, or all of them together. This template we give you the basic building blocks you need to build a VS Code extension for it.

## Programming Languages and Frameworks

The extension template has two parts, the extension part and language server part. The extension part is written in TypeScript, and language server part is written in Python over the `pygls` (Python language server) library.

For the most part you will be working on the python part of the code when using this template. You will be integrating your tool with the extension part using the [Language Server Protocol](https://microsoft.github.io/language-server-protocol). `pygls` currently works on the [version 3.16 of LSP](https://microsoft.github.io/language-server-protocol/specifications/specification-3-16/).

The TypeScript part handles working with VS Code and its UI. The extension template comes with few settings pre configured that can be used by your tool. If you need to add new settings to support your tool, you will have to work with a bit of TypeScript. The extension has examples for few settings that you can follow. You can also look at extensions developed by our team for some of the popular tools as reference.

## Requirements

1. VS Code 1.64.0 or greater
1. Python 3.7 or greater
1. node >= 14.19.0
1. npm >= 8.3.0 (`npm` is installed with node, check npm version, use `npm install -g npm@8.3.0` to update)
1. Python extension for VS Code

You should know to create and work with python virtual environments.

## Getting Started

1. Copy the contents of this template into your new project folder.
1. Create and activate a python virtual environment for this project in a terminal. Be sure to use the minimum version of python for your tool. This template was written to handle python 3.7 or greater.
1. Install `nox` in the activated environment: `python -m pip install nox`.
1. Add your favorite tool to `requirements.in`
1. Run `nox --session setup`.
1. Install test dependencies `python -m pip install -r src/test/python_tests/requirements.txt`.
1. Open `package.json`, look for and update the following things:
    1. Find and replace (case-sensitive) `<pytool>` with `mytool`. This is used as module name.
    1. Find and replace (case-sensitive) `<PyTool>` with `My Tool`. This is used as display and title name.
    1. Check the following fields and update them accordingly:
        - `"publisher"`: Update this to your publisher id from https://marketplace.visualstudio.com/.
        - `"version"`: See https://semver.org/ for details of requirements and limitations for this field.
        - `"license"`: Update license as per your project. Defaults to `MIT`.
        - `"keywords"`: Update keywords for your project, these will be used when searching in the VS Code marketplace.
        - `"categories"`: Update categories for your project, makes it easier to filter in the VS Code marketplace.
        - `"homepage"`, `"repository"`, and `"bugs"` : Update URLs for these fields to point to your project.
    1. **Optional** Add `"icon"` field with relative path to a image file to use as icon for this project.
1. Install node packages using `npm install`.

## Features of this Template

After finishing the getting started part, this template would have added the following:

1. A command `My Tool: Restart Server`.
1. Following setting:
    - `mytool.trace`
    - `mytool.args`
    - `mytool.path`
1. Following triggers for extension activation:
    - On Language `python`.
    - On File with `.py` extension found in the opened workspace.

## Adding features from your tool

Open `bundled/tool/server.py`, here is where you will do most of the work. Look for `TODO` comments there for more details.

References:

-   Protocol reference: https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/
-   Implementation showing how to handle Linting on file `open`, `save`, and `close`. [Pylint](https://github.com/microsoft/vscode-pylint/blob/main/bundled/linter)
-   Implementation showing how to handle Formatting. [Black Formatter](https://github.com/microsoft/vscode-black-formatter/blob/main/bundled/formatter)
-   Implementation showing how to handle Code Actions. [isort](https://github.com/microsoft/vscode-isort/blob/main/bundled/formatter)

## Building and Run the extension

Run the `Debug Extension and Python` configuration form VS Code. That should build and debug the extension in host window.

Note: if you just want to build you can run the build task in VS Code (`ctrl`+`shift`+`B`)

## Debugging

To debug both TypeScript and Python code use `Debug Extension and Python` debug config.

To debug only TypeScript code, use `Debug Extension` debug config.

To debug a already running server or in production server, use `Python Attach`, and select the process that is running `server.py`.

## Adding new Settings or Commands

You can add settings by contributing a configuration in `package.json` file. To pass this configuration to your python tool server (i.e, `server.py`) update the `settings.ts` as need. There are examples of different types of settings in that file that you can base your new setting on.

You can follow how `restart` command is implemented in `package.json` and `extension.ts` for how to add commands. You cam also contribute commands from Python via the Language Server Protocol.

## Testing

See `src\test\python_tests\test_server.py` for starting point. See, other referred projects here for testing various aspects of running the tool over LSP.

If you have installed the test requirements you should be able to see the tests in the test explorer.

You can also run all tests using `nox --session tests` command.

## Linting

Run `nox --session lint` to run linting on both Python and TypeScript code. Please update the nox file if you want to use a different linter and formatter.

## Packaging and Publishing

1. Update the version as need in `package.json`.
1. Build package using `nox --session build_package`.
1. Take the generated `.vsix` file and upload it to your extension management page https://marketplace.visualstudio.com/manage.

To do this from the command line see here https://code.visualstudio.com/api/working-with-extensions/publishing-extension

## Upgrading Dependencies

Dependabot yml is provided to make it easy to setup upgrading dependencies in this extension. Be sure to add the labels used in the dependabot to your repo.

To manually upgrade your local project:

1. Create a new branch
1. Run `npm update` to update node modules.
1. Run `nox --session setup` to upgrade python packages.

# Troubleshooting

## Changing path or name of `server.py` something else.

If you want to change the name of `server.py` to something else, you can. Be sure to update `constants.ts` and `src\test\python_tests\lsp_test_client\session.py`.

Also make sure that the inserted paths in `server.py` are pointing to the right folders to pick up the dependent packages.

## Module not found errors.

This can occurs if `bundled/libs` is empty. That is the folder where we put your tool and other dependencies. Be sure to follow the build steps need for creating and bundling the required libs.

Common one is `pygls` module not found.
