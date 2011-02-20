""" kinbaku.types
"""
import os
from kinbaku.report import console, report

import compiler, ast
from sourcecodegen.generation import ModuleSourceCodeGenerator,generate_code

# TODO: find a way around this monkey patch
import pep362
from pep362 import Signature as JohnHancock
class Signature(JohnHancock):
    def __len__(self):
        return len(self._parameters)

    @property
    def has_default_values(self):
        return any([hasattr(p,'default_value') for p in self._parameters.values()])

    @property
    def default_values(self):
        items = [[k,v] for k,v in self._parameters.items() if hasattr(v,'default_value')]
        return dict([[k, v.default_value] for k,v in items])
pep362.Signature=Signature

class FileCoverage:
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

    def lines_missing_from_coverage(self):
        """ returns [lineno,line] for lines that lack coverage """
        content_raw  = open(self.fname,'r').read()
        dammit = compiler.parse(content_raw)
        def walk(node,parent=None):
            """ walker for ast rooted at <node> """
            #print node
            if node is None: pass
            elif isinstance(node,str): pass#rint node
            elif isinstance(node,int): pass#rint node
            else:
                if isinstance(node,list):
                    [ walk(child,parent=node) for child in node ]
                elif isinstance(node,tuple):
                    [ walk(child,parent=node) for child in node ]
                else:
                    if hasattr(node,'lineno') and node.lineno in self.linenos:
                        src_code = generate_code(parent).strip()
                        if node.lineno in results:   results[node.lineno] += [src_code]
                        else:                        results[node.lineno]  = [src_code]
                    [ walk(child,parent=node) for child in node.getChildren() ]
        results = {}; walk(dammit)

        out = []
        for lineno in results:
            cleaned = [ [len(src), src] for src in results[lineno] ]
            out.append([lineno, cleaned[0][1]])
        return out

    def objects_missing_from_coverage(self):
        """ returns [lineno,line] for lines that lack coverage """
        content_raw  = open(self.fname,'r').read()
        dammit = compiler.parse(content_raw)
        def walk(node,parent=None,lineage=[]):
            """ walker for ast rooted at <node> """
            #print node
            if node is None: pass
            elif isinstance(node,str): pass#rint node
            elif isinstance(node,int): pass#rint node
            else:

                if isinstance(node,list):
                    [ walk(child,parent=node,lineage=lineage+[parent]) for child in node ]
                elif isinstance(node,tuple):
                    [ walk(child,parent=node,lineage=lineage+[parent]) for child in node ]
                else:
                    #from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
                    if hasattr(node,'lineno') and node.lineno in self.linenos:
                        src_code = generate_code(lineage[-1]) # source for container
                        src_code = src_code.split('\n')[0] #strip()
                        src_code = console.color(src_code).strip()
                        if node.lineno in results:   results[node.lineno] += [src_code]
                        else:                        results[node.lineno]  = [src_code]
                    [ walk(child,parent=node,lineage=lineage+[parent]) for child in node.getChildren() ]
        results = {}; walk(dammit)

        out = []
        for lineno in results:
            cleaned = [ [len(src), src] for src in results[lineno] ]
            out.append([lineno, cleaned[0][1]])
        return out
        #from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()

    def __str__(self):
        return "<Coverage: {stuff}>".format(stuff=str([self.fname,self.cover]))

class UnusableCodeError(ValueError):
    pass

class Comment(object):
    def rparent(self):
        pass

    def rowner(self):
        """ render owner """
        if isinstance(self.owner,str): return self.owner
        p  = self.owner.parent or ''
        pp = p and p.parent or ''
        ppp = pp and pp.parent or ''
        p = p and p[0].tagname
        pp = pp and pp[0].tagname
        ppp = ppp and ppp[0].tagname
        def fmt(x):
            if not x: return
            if isinstance(x,str):
                return x,x
            return x.tagname, str(x[0].astext()).strip()
        # eg: [('class_section', 'CBPlugin'), ('method_section', 'files')]
        tmp = [fmt(self.owner.parent), fmt(self.owner),]
        tmp = filter(None,tmp)
        tmp = [tpl[1] for tpl in tmp]
        tmp= '.'.join(tmp)
        return tmp


    def __str__(self):
        dox = console.color(self.text).rstrip()
        return '{lineno}:\t{dox}'.format(lineno=self.lineno,
                                          dox=dox, )
    def display(self):
        print str(self)

    def __init__(self,lineno=-1, text='', full_line=False,owner='??'):
        self.owner     = owner
        self.lineno    = int(lineno)
        self.text      = text
        self.full_line = full_line

class Match(object):
    def __str__(self):
        return 'Match_'+str(self.__dict__)

    __repr__=__str__

    def __init__(self, **kargs):
        for k,v in kargs.items(): setattr(self,k,v)
