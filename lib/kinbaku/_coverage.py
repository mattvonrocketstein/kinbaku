""" kinbaku._coverage
"""
import os

import compiler, ast
from sourcecodegen.generation import ModuleSourceCodeGenerator,generate_code

from kinbaku.report import console
from kinbaku._ast import node_has_lineno,walk

class KinbakuFile(object):
    @property
    def contents(self):
        return open(self.fname,'r').read()

    @property
    def ast(self):
        return compiler.parse(self.contents)

class FileCoverage(KinbakuFile):
    """ tracks coverage metadata for a specific file """
    def __init__(self, linenos=[], fname='', original_line='',
                 statements=0, miss=0,cover=0):
        self.linenos=linenos
        self.fname=fname
        if not os.path.exists(self.fname) and not\
               self.fname.endswith('.py'):
            self.fname+='.py'
        self.statements=statements
        self.original_line=original_line
        self.miss=miss
        self.cover=cover

    def node_in_missed_lines(self,node):
        return node_has_lineno(node) and node.lineno in self.linenos

    def lines_missing_from_coverage(self):
        """ returns [lineno,line] for lines that lack coverage """
        def tree2src(node,parent,lineage):
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

        results = {}; walk(self.ast, test=self.node_in_missed_lines,
                           callback=callback, )

        out = []
        for lineno in results:
            cleaned = [ [len(src), src] for src in results[lineno] ]
            out.append([lineno, cleaned[0][1]])
        return out

    def objects_missing_from_coverage(self):
        """ returns [lineno,line] for lines that lack coverage """

        def tree2src(node, parent,lineage):
            """ """
            if not lineage: return 'ZZ:'+str(node)
            gpa = lineage[-1]

            #if isinstance(gpa,compiler.ast.If):
            #    return tree2src(node,parent,lineage[:-1])
            if isinstance(gpa,(compiler.ast.Function,
                               compiler.ast.Class)):
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
        test = lambda node: node_has_lineno(node) and node.lineno in self.linenos
        results = {}
        walk(self.ast, test=test, callback=callback, )

        out = []
        for lineno in results:
            cleaned = [ [len(src), src] for src in results[lineno] ]
            out.append([lineno, cleaned[0][1]])
        return out
        #from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()

    def __str__(self):
        return "<Coverage: {stuff}>".format(stuff=str([self.fname,self.cover]))
