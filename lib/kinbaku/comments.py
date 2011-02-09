""" kinbaku.comments
"""
import sys
from path import path

from docutils.readers.python.moduleparser import parse_module

from kinbaku.report import console, report
from kinbaku.plugin import KinbakuPlugin, publish_to_commandline
from kinbaku.codebase import plugin as CodeBase

strip_string_markers = lambda line: line.replace('"','').replace("'",'')
def extract_comments(content_lines):
    """
    ## derive comment strings, correlate them with line numbers:
    ##  [ [lineN, comment1], [lineM, comment2], .. ]
    """
    comments  = []
    contents_raw3 = content_lines
    for line in contents_raw3:
        if '#' in line:
            line2 = line[line.find('#'):]
            comments.append([[contents_raw3.index(line),line2]])
    return comments
def extract_docstrings(content_raw,name):
    """
    ## derive document strings:
    ##  [ [line1_comment1,line2_comment1], [line1_comment2],.. ]
    """
    dox2      = []
    doctree   = [ x for x in parse_module(content_raw, name) ]
    doctree   = [ x for x in doctree if x.tagname=='docstring' ]
    dox       = [ x[0].astext().split('\n') for x in doctree ]
    out       = [strip_string_markers(line) for line in content_raw.split('\n')]

    ## correlate docstrings to line numbers
    ##  [ [[lineX, line1_comment1 ], [lineX+1, line2_comment1, ], [ [lineY, line1_comment2,],.. ]
    for docstring in dox:
        row = []
        for line in docstring:
            try: lineno = out.index(line + '\n')
            except ValueError: lineno='?'
            if line.strip():
                row.append([lineno, line])
        dox2.append(row)
    return dox2

class CommentsExtractor(KinbakuPlugin):
    """ """
    @classmethod
    def spawn(kls, **kargs):
        return CommentsExtractor()

    @publish_to_commandline
    def extract(self, input_file_or_dir):
        """ extracts both module/class/function documentation,
            as well as comments and displays them in order """

        def display_file(fpath):
            print console.blue('{fpath}'.format(fpath=fpath))
        def display_comment(lineno,dox):
            print '  {lineno}:\t{dox}'.format(lineno=lineno,
                                              dox=console.color(dox).rstrip())

        with CodeBase(input_file_or_dir, gloves_off=True, workspace=None) as codebase:
            self.codebase = codebase
            for fpath in codebase.python_files:
                # TODO: validate file

                fhandle       = lambda: open(fpath)
                content_raw   = fhandle().read()
                content_lines = fhandle().readlines()

                docstrings  = extract_docstrings(content_raw, fpath.name)
                comments    = extract_comments(content_lines)

                ## merge lists by line number
                out = docstrings + comments
                out.sort(lambda x,y: cmp(x[0][0],y[0][0]))

                ## display results
                display_file(fpath)
                for doc_group in out:
                    for doc in doc_group:
                        lineno,dox = doc
                        display_comment(lineno,dox)
                    #if len(doc_group)>1:
                    #    print '  ',console.divider(display=False)

plugin=CommentsExtractor
