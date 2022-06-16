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
1. npm >= 8.3.0 (node comes with npm 6.\* use `npm install -g npm@8.3.0` to update)

You should know to create and work with a python virtual environment.

## How do I build and extension for my favorite tool?

**This is not ready yet**

1. Create a new repository for your new extension.
1. Copy the contents of this template into your new repo.
1. Create and activate the virtual environment for this project in a terminal.
1. Add your favorite tool to `requirement.in`, and `pip-compile` it to generate `requirement.txt`.
1. Install packages from pip using the generated `requirements.txt`.
1. Install node packages using `npm install`.
1. Open `package.json`, look for and update the following things:
    1. Find and replace (case-sensitive) `<pytool>` with `yourtool`. This is used as module name.
    1. Find and replace (case-sensitive) `<PyTool>` with `Your Tool`. This is used as display and title name.
    1. Find and replace (case-sensitive) `<pytool-publisher>` with your publisher id from https://marketplace.visualstudio.com/.
    1. Find and replace (case-sensitive) `<pytool-repo>` with your git repository path.
    1. Check the `"version"`, `"license"`, `"keywords"`, and `"categories"` fields, and set them as appropriate for your tool.
    1. **Optional** Add `"icon"` field with relative path to a image file to use as icon for this project.
1. Open `bundled/tool/server.py`, here is where you will do most of the work.
    - Protocol reference: https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/
    - Implementation showing how to handle Linting on file `open`, `save`, and `close`. [Pylint](https://github.com/microsoft/vscode-pylint/blob/main/bundled/linter)
    - Implementation showing how to handle Formatting. [Black Formatter](https://github.com/microsoft/vscode-black-formatter/blob/main/bundled/formatter)
    - Implementation showing how to handle Code Actions. [isort](https://github.com/microsoft/vscode-isort/blob/main/bundled/formatter)

## Building the extension?

1. This you will need to do any time you add a new tool or want to update the version:
    1. Install `nox` into your python environment.
    1. Ensure that your `requirements.txt` is up to date.
    1. Run `nox --session install_bundled_libs` to bundle your tool with the extension.
1. Run the "Run Extension" configuration form VS Code. That should build and run the extension in host window.

## How do I debug the extension?

To debug the Type script parts just set a breakpoint in the TS files and use the "Run Extension" debug config.

To debug python files, after the extension has started using "Run Extension", use the "Python: Attach" config, and select the process that is running `server.py`.

## How do I write tests?

See `src\test\python_tests\test_server.py` for starting point. See, other referred projects here for testing various aspects of running the tool over LSP.

## How do I package for publishing on marketplace?

Run `nom run vsce-package` from terminal. That should build a package that you can upload to the market place.

## Troubleshooting

### Changing path or name of `server.py` something else.

If you want to change the name of `server.py` to something else you can. Be sure to update `constants.ts` and `src\test\python_tests\lsp_test_client\session.py`.

Also make sure that the inserted paths in `server.py` are pointing to the right thing to pick up the packages.

### Module not found errors.

This can occurs if `bundled/libs` is empty. That is the folder where we put your tool and other dependencies. Be sure to follow the build steps need for creating and bundling the required libs.
