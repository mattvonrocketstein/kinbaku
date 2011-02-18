""" kinbaku.codebase.search

      helpers for searching ast's
"""
import compiler
from compiler.ast import Node, Import,From,CallFunc,Name,Getattr
from sourcecodegen import ModuleSourceCodeGenerator
from kinbaku import codegen
from kinbaku.codebase.walkers import walker as W
from kinbaku.report import console
from kinbaku import codegen

def visit(n): pass
def src2ast(src):     return compiler.parse(src)
def fpath2ast(fpath): return src2ast(open(fpath).read())
def ast2src(x):       return ModuleSourceCodeGenerator(x).getSourceCode()
is_import = lambda n:isinstance(n,tuple((From,Import)))
is_call   = lambda n:isinstance(n,CallFunc)

class ImportFilter(object):
    """ """
    def __init__(self):
        self.import_roots    = []
        self.from_imports    = []

    @property
    def aliased_imports(self):
        return [ [prefix,name,alias] for \
                  prefix,name,alias in self.from_imports if alias ]

    def show(self):
        """ """
        print self.import_roots

    def __call__(self, n):
        """ n is compiler.ast.Node """
        if isinstance(n, Import):
            names = [x[0] for x in n.asList()[0]]
            [ self.import_roots.append(name) for name in names ]
        elif isinstance(n, From):
            modpath_prefix,_,__ = n.asList()
            modpath,alias = _[0]
            self.import_roots.append(modpath_prefix)
            self.from_imports.append([modpath_prefix, modpath, alias])
        return self

class Filter(object):
    """ """
    def __init__(self):
        self.accumulator = []
        self.accumulator2 = []
    def __call__(self, n):
        self.accumulator.append(n)

class CallFilter(Filter):
    """ """
    def __init__(self):
        Filter.__init__(self)
    def __call__(self, n):
        first = n.getChildren()
        first = first and first[0]
        if first:
            if isinstance(first, Name):
                self.accumulator.append(n)
            elif isinstance(first, Getattr):
                self.accumulator2.append(n)
            else: pass#rint n
        else:     pass#rint n

    @property
    def simple(self):
        return [ast2src(n) for n in self.accumulator]

    @property
    def complex(self):
        return [ast2src(n) for n in self.accumulator2]

    def show(self):
        """ """
        print console.blue('simple calls')
        #console.divider()
        simple_calls=self.simple
        simple_calls.sort()
        for cc in simple_calls: print cc

        print console.blue('complex calls')
        #console.divider()
        complex_calls = self.complex
        complex_calls.sort()
        for cc in complex_calls: print cc

def imports(codebase, fpath, simple=True):
    """ show imports for file @ fpath """
    ifilter = ImportFilter()
    filters = { is_import : lambda n:ifilter(n), }
    W(fpath2ast(fpath), blammo=visit, filters=filters)
    ifilter.show()

def functions(codebase, fpath, simple=True):
    """ show imports for file @ fpath """
    foo = compiler.parse(open(fpath).read())
    cfilter = CallFilter()
    filters = { is_call : lambda n:cfilter(n), }
    W(foo, blammo=visit, filters=filters)
    cfilter.show()
