"""
Copyright (c) 2011-2013 F-Secure
See LICENSE for details

Wrapper around graphviz, simply does the command line invocations
"""

from murphy.utils import execute_command

_GRAPHVIZ_EXE = (r'\Program Files (x86)\Graphviz2.32\bin\dot.exe')

def generate_imap_and_png(file_name):
    """Invokes graphviz and generates a png and an ismap file for the given
    dot file, the resulting files are called file_name.png and file_name.ismap
    """
    execute_command(_GRAPHVIZ_EXE, ['-Tismap', '-Tpng', '-O', file_name])

def generate_svg(file_name):
    """Invokes graphviz and generates a png and an ismap file for the given
    dot file, the resulting files are called file_name.png and file_name.ismap
    """
    execute_command(_GRAPHVIZ_EXE, ['-Tsvg', '-O', file_name])
