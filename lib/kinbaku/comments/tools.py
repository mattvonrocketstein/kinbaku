""" kinbaku.comments.tools
"""
import compiler
from StringIO import StringIO
from docutils.readers.python.moduleparser import parse_module
import sourcecodegen

from kinbaku._ast import walk
from kinbaku._ast import node_is_function, node_is_module
from kinbaku._ast import dotpath2ast, dotpath2obj
from kinbaku.python import Comment
from kinbaku.core import KinbakuFile
from kinbaku._types import BadDotPath

strip_string_markers = lambda line: line.replace('"','').replace("'",'')
from kinbaku._ast import src2stringio

def inject_comments(comments, src_code, dotpath):
    """ injects comments into src_code @ the function
        described by func_dotpath.

        NOTE: this function may involve dynamic analysis
    """
    src,node = dotpath2ast(src_code, dotpath)
    #print node.body
    from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()

def extract_comments(content_lines):
    """ docutil does not appear to provide a way to do this.
         ## derive comment strings, correlate them with line numbers:
         ##  [ [lineN, comment1], [lineM, comment2], .. ]
    """
    comments  = []
    contents_raw3 = content_lines
    for line in contents_raw3:
        if '#' in line:
            line2 = line[line.find('#'):]
            #comments.append([[contents_raw3.index(line),line2]])
            comments.append([Comment(lineno=contents_raw3.index(line),
                                     text=line2, owner="hash-comment",
                                     full_line=line.strip()==line2.strip())])
    return comments

def extract_docstrings(content_raw,name):
    """ extracts docstrings
         ## derive document strings:
         ##  [ [line1_comment1,line2_comment1], [line1_comment2],.. ]
    """
    dox2         = []
    lines        = content_raw.split('\n')
    doctree      = parse_module(content_raw, name)
    doctree_list = doctree.traverse()
    doctree_list = [ x for x in doctree_list if x.tagname=='docstring' ]
    dox          = [ [ x.parent,                  # What the comment is for
                       x[0].astext().split('\n'), # What the comment actually *is*
                      ] \
                     for x in doctree_list ]
    #from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
    tmp          = [strip_string_markers(line) for line in lines]
    tmp_stripped = [x.strip() for x in tmp]

    ## correlate docstrings to line numbers
    ##  [ [[lineX, line1_comment1 ], [lineX+1, line2_comment1, ], [ [lineY, line1_comment2,],.. ]
    for parent, docstring in dox: # [x[-1] for x in dox]:
        row = []
        for line in docstring:
            try:
                lineno = tmp_stripped.index(strip_string_markers(line).strip())
            except ValueError:
                lineno='-1'
                raise Exception, [strip_string_markers(line), tmp[8:12]]
            if line.strip():
                row.append(Comment(lineno=lineno,
                                   text=line,
                                   owner=parent,
                                   full_line=True))
        if row: dox2.append(row)
    return dox2

if __name__=='__main__':
    #x = inject_comments('test1\ntest2', 'def f(a,b): return 3', 'f')
    x = inject_comments('test1\ntest2', 'class zoo:\n def f(a,b):\n  "test"\n  return 3', 'zoo.f')

    #from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
    #from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
