# Template for VS Code python tools extensions

This is a template repository to get you started on building a VS Code extension for your favorite python tool. It code be a linter, formatter, or code analysis, or all of them together. This template we give you the basic building blocks you need to build a VS Code extension for it.

## Which languages do you need to know?

Python for the most part. A major part of the what you need to do to integrate your tool into this template exists in python parts of the template.

TypeScript for adding new settings and commands. If you need to add new settings to support your tool, you will have to work with a bit of TypeScript. The extension has examples for various settings you can follow that. You can also look at extensions developed by our team for some of the popular tools as reference.

We are here to help, and you can ask us for input.

## What do I need to have?

You will need the following things:

1. VS Code
1. Python 3.7 or greater
1. node >= 14.19.0
1. npm >= 8.3.0 (check npm version, use `npm install -g npm@8.3.0` to update)

You should know to create and work with a python virtual environment.

## How do I setup the template for my favorite tool?

1. Create a new repository for your new extension.
1. Copy the contents of this template into your new repo.
1. Create and activate the virtual environment for this project in a terminal. Be sure to use the minimum version of python for your tool. This template was written to handle python 3.7 or greater.
1. Add your favorite tool to `requirements.in`, and `pip-compile` it to generate `requirements.txt`. See `requirements.in` file for more details.
1. `pip-compile` test requirements as well. See `src/test/python_tests/requirements.in`.
1. Install `nox` into your python environment.
    1. Run this to install all dependencies needed for your tool in a packageable way `nox --session install_bundled_libs`.
    1. Run this to install all test dependencies: `python -m pip install -r src/test/python_tests/requirements.txt`.
1. Open `package.json`, look for and update the following things:
    1. Find and replace (case-sensitive) `<pytool>` with `yourtool`. This is used as module name.
    1. Find and replace (case-sensitive) `<PyTool>` with `Your Tool`. This is used as display and title name.
    1. Check the following fields and update them accordingly:
        - `"publisher"`: Update this to your publisher id from https://marketplace.visualstudio.com/.
        - `"version"`: See https://semver.org/ for details of requirements and limitations for this field.
        - `"license"`: Update license as per your project. Defaults to `MIT`.
        - `"keywords"`: Update keywords for your project, these will be used when searching in the VS Code marketplace.
        - `"categories"`: Update categories for your project, makes it easier to filter in the VS Code marketplace.
        - `"homepage"`, `"repository"`, and `"bugs"` : Update URLs for these fields to point to your project.
    1. **Optional** Add `"icon"` field with relative path to a image file to use as icon for this project.
1. Install node packages using `npm install`.

## Where do I add features from my favorite tool?

1. Open `bundled/tool/server.py`, here is where you will do most of the work.
    - Protocol reference: https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/
    - Implementation showing how to handle Linting on file `open`, `save`, and `close`. [Pylint](https://github.com/microsoft/vscode-pylint/blob/main/bundled/linter)
    - Implementation showing how to handle Formatting. [Black Formatter](https://github.com/microsoft/vscode-black-formatter/blob/main/bundled/formatter)
    - Implementation showing how to handle Code Actions. [isort](https://github.com/microsoft/vscode-isort/blob/main/bundled/formatter)

## How do I build and run the extension?

1. This you will need to do any time you add a new tool or want to update the version:
    1. Install `nox` into your python environment.
    1. Ensure that your `requirements.txt` is up to date.
    1. Run `nox --session install_bundled_libs` to bundle your tool with the extension.
1. Run the `Debug Extension and Python` configuration form VS Code. That should build and debug the extension in host window.

## How do I debug the extension?

To debug both TypeScript and Python code use `Debug Extension and Python` debug config.

To debug only TypeScript code, use `Debug Extension` debug config.

To debug a already running server or in production server, use `Python Attach`, and select the process that is running `server.py`.

## How do I add new settings?

You can add settings by contributing a configuration in `package.json` file. To pass this configuration to your python tool server (i.e, `server.py`) update the `settings.ts` as need. There are examples of different types of settings in that file that you can base your new setting on.

## How do I write tests?

See `src\test\python_tests\test_server.py` for starting point. See, other referred projects here for testing various aspects of running the tool over LSP.

## How do I package for publishing on marketplace?

Run `npm run vsce-package` from terminal. That should build a package that you can upload to the marketplace. Ensure that you have updated all the required fields for publishing packages to marketplace.

## Troubleshooting

### Changing path or name of `server.py` something else.

If you want to change the name of `server.py` to something else, you can. Be sure to update `constants.ts` and `src\test\python_tests\lsp_test_client\session.py`.

Also make sure that the inserted paths in `server.py` are pointing to the right folders to pick up the dependent packages.

### Module not found errors.

This can occurs if `bundled/libs` is empty. That is the folder where we put your tool and other dependencies. Be sure to follow the build steps need for creating and bundling the required libs.

Common one is `pygls` module not found.
