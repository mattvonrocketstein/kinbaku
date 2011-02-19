""" kinbaku.comments
"""
import sys
from path import path

from docutils.readers.python.moduleparser import parse_module

from kinbaku.report import console, report
from kinbaku.plugin import KinbakuPlugin, publish_to_commandline
from kinbaku.codebase import plugin as CodeBase
from kinbaku._types import Comment

strip_string_markers = lambda line: line.replace('"','').replace("'",'')

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
    """
    ## derive document strings:
    ##  [ [line1_comment1,line2_comment1], [line1_comment2],.. ]
    """
    dox2         = []
    lines        = content_raw.split('\n')
    doctree      = parse_module(content_raw, name)
    doctree_list = doctree.traverse()#[ x for x in parse_module(content_raw, name) ]
    doctree_list = [ x for x in doctree_list if x.tagname=='docstring' ]

    dox          = [ [ x.parent,               # What the comment is for
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

class CommentsExtractor(KinbakuPlugin):
    """ """
    @classmethod
    def spawn(kls, **kargs):  return CommentsExtractor()

    @publish_to_commandline
    def ratio(self, input_file_or_dir):
        """ extract comment:code ratios """
        if path(input_file_or_dir).isdir():
            for fpath in [x for x in path(input_file_or_dir).files() if x.endswith('.py')]:
                print fpath
                self.ratio(fpath)
                print
                print
            return

        fpath,groups = self._extract(input_file_or_dir)
        if groups:
            count        = [ [1 for comment in group] for group in groups]
            num_comments = sum([sum(subcount) for subcount in count ])
            total_lines  = len(open(input_file_or_dir).readlines())
            nratio       = str(1.0*num_comments/total_lines)[:5]

            msg0 = "  ratio {T}".format(T=nratio)
            msg1 = "  total_lines {T}".format(T=total_lines)
            msg2 = "  total_comment_lines {N}".format(N=num_comments)
            msg3 = "  total_comments {K}".format(K=len(groups))
            msg4 = "  avg_lines_group {M}".format(M=num_comments*1.0/len(groups))
            #from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
            print msg0
            print msg3
            print msg1
            print msg2
            print msg4

    @publish_to_commandline
    def extract(self, input_file_or_dir, comments=False,docstrings=False):
        """ extract comments, organized by container.
            if --docstrings is True, only docstring-style comments will be displayed.
            if --comments is True, only hash-mark style comments will be displayed.
            default is to show both.
        """
        fpath, lst_of_comment_lsts = self._extract(input_file_or_dir,comments=comments,docstrings=docstrings)

        ## display results
        print console.blue('{fpath}'.format(fpath=fpath))
        for comment_lst in lst_of_comment_lsts:
            owner_display = console.blue(comment_lst[0].rowner())
            print '\nin "{owner}":'.format(owner=owner_display)
            print '\n'.join([str(comment) for comment in comment_lst])

    def _extract(self, input_file_or_dir, comments=True, docstrings=True):
        """ """
        if not comments and not docstrings:
            comments = docstrings = True
        with CodeBase(input_file_or_dir, gloves_off=True, workspace=None) as codebase:
            self.codebase = codebase
            for fpath in codebase.python_files:
                # TODO: validate file
                fhandle       = lambda: open(fpath)
                content_raw   = fhandle().read()
                content_lines = fhandle().readlines()

                doc_strings = extract_docstrings(content_raw, fpath.name)
                komments    = extract_comments(content_lines)

                ## merge lists by line number
                out = []
                if docstrings: out+=doc_strings
                if comments: out+=komments
                out.sort(lambda x,y: cmp(x[0].lineno, y[0].lineno))
                return fpath, out
plugin = CommentsExtractor

if __name__=='__main__':
    from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
