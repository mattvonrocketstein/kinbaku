""" kinbaku.types
"""
import os
from kinbaku.report import console, report
from kinbaku._coverage import FileCoverage


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
pep362.Signature=Signature # TODO: find a way around this monkey patch


class UnusableCodeError(ValueError): pass

class Comment(object):
    def rparent(self): pass

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
