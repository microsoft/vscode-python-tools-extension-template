# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
All the action we need during build
"""

import nox  # pylint: disable=import-error


def _install_bundle(session: nox.Session):
    session.install(
        "-t",
        "./bundled/libs",
        "--no-cache-dir",
        "--implementation",
        "py",
        "--no-deps",
        "--upgrade",
        "-r",
        "./requirements.txt",
    )


def _setup_template_environment(session: nox.Session):
    session.install("wheel", "pip-tools")
    session.run("pip-compile", "--generate-hashes", "--upgrade", "./requirements.in")
    session.run(
        "pip-compile",
        "--generate-hashes",
        "--upgrade",
        "./src/test/python_tests/requirements.in",
    )
    _install_bundle(session)


@nox.session(python="3.7")
def setup(session: nox.Session):
    """Sets up the template for development."""
    _setup_template_environment(session)


@nox.session()
def tests(session: nox.Session):
    """Runs all the tests for the extension."""
    session.install("-r", "src/test/python_tests/requirements.txt")
    session.run("pytest", "src/test/python_tests")


@nox.session()
def lint(session: nox.Session):
    """Runs linter and formatter checks on python files."""
    session.install("-r", "./requirements.txt")
    session.install("-r", "src/test/python_tests/requirements.txt")

    session.run("pylint", "./bundled/tool")
    session.run(
        "pylint",
        "--ignore=./src/test/python_tests/test_data",
        "./src/test/python_tests",
    )
    session.run("pylint", "noxfile.py")

    # check formatting using black
    session.install("black")
    session.run("black", "--check", "./bundled/tool")
    session.run("black", "--check", "./src/test/python_tests")
    session.run("black", "--check", "noxfile.py")

    # check import sorting using isort
    session.install("isort")
    session.run("isort", "--check", "./bundled/tool")
    session.run("isort", "--check", "./src/test/python_tests")
    session.run("isort", "--check", "noxfile.py")

    # check typescript code
    session.run("npm", "run", "lint", external=True)


@nox.session()
def build_package(session: nox.Session):
    """Builds VSIX package for publishing."""
    _setup_template_environment(session)
    session.run("npm", "install", external=True)
    session.run("npm", "run", "vsce-package", external=True)
