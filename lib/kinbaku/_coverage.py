""" kinbaku._coverage

    from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
"""
import os
import StringIO

import compiler, ast
from coverage.cmdline import main,CoverageScript
from sourcecodegen.generation import generate_code
from sourcecodegen.generation import ModuleSourceCodeGenerator

from kinbaku.report import console
from kinbaku._ast import node_has_lineno,walk
from kinbaku._types import KinbakuFile

OLD_BANNER = '----------------------------------------------------------------------------------'

def convert(x):
    """ converts ast node lineno's to either
        integers or tuples of integers """
    if not x: return
    try: return int(x)
    except ValueError:
        return map(int,x.split('-'))

def mine_cvg_output(line):
    """ """
    cvg_output_line   = line.split()
    miss,  cover      = cvg_output_line[2],cvg_output_line[3]
    fname, statements = cvg_output_line[0],cvg_output_line[1]
    linenos           = ''.join(cvg_output_line[4:]).split(',')
    linenos           = map(convert, linenos)

    # NOTE: cuts off the "missed lines" bit, it's stored in "linenos"
    original_line = line.split('%')[0]+'%'

    # HACK: because of coverage's default output style
    if not os.path.exists(fname) and not fname.endswith('.py'):
        fname += '.py'

    return fname, miss,cover,linenos,original_line,statements

class FileCoverage(KinbakuFile):
    """ tracks coverage metadata for a specific file """
    def __init__(self, linenos=[], fname='', original_line='',
                 statements=0, miss=0,cover=0):
        KinbakuFile.__init__(self,fname=fname)
        self.linenos       = linenos
        self.statements    = statements
        self.original_line = original_line
        self.miss  = miss
        self.cover = cover

    def node_in_missed_lines(self,node):
        return node_has_lineno(node) and node.lineno in self.linenos

    def lines_missing_from_coverage(self):
        """ returns [lineno,line] for lines that lack coverage """
        def tree2src(node, parent, lineage):
            try:
                return generate_code(parent).strip()
            except Exception,e:
                err=str(e)
                err = "err:{E} -- {T}".format(E=err, T=str([type(e)]))
                return err

        def callback(node, parent, lineage):
            src_code = tree2src(node,parent,lineage)
            lineno   = node.lineno
            if node.lineno in results:   results[lineno] += [src_code]
            else:                        results[lineno]  = [src_code]

        out = []; results = {};
        walk(self.ast, test=self.node_in_missed_lines, callback=callback, )

        for lineno in results:
            cleaned = [ [len(src), src] for src in results[lineno] ]
            out.append([lineno, cleaned[0][1]])
        return out

    def objects_missing_from_coverage(self):
        """ experimental: show objects instead of lineno's
            returns [lineno, line] for lines that lack coverage """

        def tree2src(node, parent, lineage):
            """ convert node/parent/lineage to src-code  """
            if not lineage: return 'ZZ:'+str(node)
            gpa = lineage[-1]

            #if isinstance(gpa,compiler.ast.If):
            #    return tree2src(node,parent,lineage[:-1])
            if isinstance(gpa,(compiler.ast.Function, compiler.ast.Class)):
                try:
                    src_code = generate_code(gpa) # source for container
                except Exception,e:
                    return "err:{err}".format(err=str(e))
                src_code = src_code.split('\n')[0]
                src_code = console.color(src_code).strip()
                return src_code
            elif isinstance(gpa,(compiler.ast.Module)):
                return "MODULE"
            elif isinstance(gpa,(compiler.ast.If,compiler.ast.Stmt)):
                return tree2src(node,parent,lineage[:-1])
            else:
                return str((gpa.__class__,))

        def callback(node, parent, lineage):
            src_code = tree2src(node,parent,lineage)
            lineno   = node.lineno
            if lineno in results:   results[lineno] += [src_code]
            else:                   results[lineno]  = [src_code]
        out = []; results = {}
        walk(self.ast, test=self.node_in_missed_lines, callback=callback, )

        for lineno in results:
            cleaned = [ [len(src), src] for src in results[lineno] ]
            out.append([lineno, cleaned[0][1]])
        return out


    def __str__(self):
        return "<Coverage: {stuff}>".format(stuff=str([self.fname,self.cover]))
