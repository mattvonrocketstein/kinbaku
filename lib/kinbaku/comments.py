""" kinbaku.comments
"""
import sys
from path import path

from docutils.readers.python.moduleparser import parse_module

from kinbaku.report import console, report
from kinbaku.plugin import KinbakuPlugin, publish_to_commandline

class CommentsExtractor(KinbakuPlugin):
    """ """
    @classmethod
    def spawn(kls, **kargs):
        return CommentsExtractor()

    @publish_to_commandline
    def extract(self, input_file_or_dir):
        """ extracts both module/class/function documentation,
            as well as comments and displays them in order """
        from kinbaku.codebase import plugin as CodeBase
        with CodeBase(input_file_or_dir, gloves_off=True, workspace=None) as codebase:
            self.codebase = codebase
            for fpath in codebase.python_files:
                print console.blue('{fpath}'.format(fpath=fpath))
                # validate file
                contents  = open(fpath).read()
                contents2 = [line.replace('"','').replace("'",'') for line in open(fpath).readlines()]
                doctree   = [ x for x in parse_module(contents,fpath.name) ]
                dox       = [ x[0].astext().split('\n') for x in doctree if x.tagname=='docstring' ]
                dox2      = []
                for docstring in dox:
                    docstring2=[]
                    for line in docstring:
                        try: lineno = contents2.index(line+'\n')
                        except ValueError: lineno='?'
                        if line.strip():
                            docstring2.append([lineno,line])
                    dox2.append(docstring2)
                comments  = []
                contents3 = open(fpath).readlines()
                for line in contents3:
                    if '#' in line:
                        line2 = line[line.find('#'):]
                        comments.append([[contents3.index(line),line2]])
                ## merge lists by lineno
                dox3 = dox2+comments
                dox3.sort(lambda x,y: cmp(x[0][0],y[0][0]))

                for doc_group in dox3:
                    for doc in doc_group:
                        lineno,dox = doc
                        print '  {lineno}:\t{dox}'.format(lineno=lineno,dox=console.color(dox).rstrip())
                    #if len(doc_group)>1:
                    #    print '  ',console.divider(display=False)

plugin=CommentsExtractor
