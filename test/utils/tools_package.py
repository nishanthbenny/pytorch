"""Allows test code to reliably import from <repo-root>/tools/.

Why does this exist?
We want to be able to write unit tests for the tools/ code and we want
it to work when PyTorch is installed or installed for develop.

Because of the way "python setup.py develop" is implemented, importing
from tools/ just works. The develop installation method pip installs a
symlink that points to the pytorch repository root. This allows for
importing the torch package and incidentally also allows for importing
tools.

However, if you install via "python setup.py install", you *only* get
the torch package installed. Importing tools will not succeed. This is
how CI installs pytorch.

Importing this module bootstraps the finding of tools by importing
just the tools module. Subsequent imports follow that module as if it
were a package.

This is only approved for use in PyTorch tests.

Example (in some test file):
  from utils.tools_package import tools

  # Add whatever imports below tools make sense here, e.g.
  import tools.codegen.model

REQUIRES: must be imported from a pytorch clone with tools included.
"""

import importlib.util
import pathlib
import sys


def _import_tools_module():
    """Imports and returns the tools module."""
    # We expect this file to be
    # <repo-root>/test/utils/tools_package.py, so we have to go up two
    # levels to find the repository root.
    PYTORCH_DIR = pathlib.Path(__file__).parent.parent.parent

    # The tools/ "package" is right below the root.
    TOOLS_DIR = PYTORCH_DIR / 'tools/'
    if not TOOLS_DIR.is_dir():
        raise FileNotFoundError(
            'We did not successfully locate the tools/ directory. This is most '
            'likely because this PyTorch clone does not contain this directory '
            'or files were moved around. Read the comments on the function that '
            'raised this assertion for more information.')

    # This recipe comes from
    # https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly
    spec = importlib.util.spec_from_file_location('tools',
                                                  TOOLS_DIR / '__init__.py')
    tools = importlib.util.module_from_spec(spec)
    sys.modules['tools'] = tools
    # Execute the module, in case it executes any code upon import.
    spec.loader.exec_module(tools)

    return tools


# Unconditionally import the tools module: that's what importing this
# module is designed to do.
tools = _import_tools_module()
