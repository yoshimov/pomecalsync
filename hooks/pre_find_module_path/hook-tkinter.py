import os
import sys


def pre_find_module_path(hook_api):
    stdlib_dir = os.path.join(sys.base_prefix, 'Lib')
    tkinter_dir = os.path.join(stdlib_dir, 'tkinter')
    if os.path.isdir(tkinter_dir):
        hook_api.search_dirs = [stdlib_dir]
