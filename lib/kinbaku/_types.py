""" kinbaku.types
"""
from kinbaku.report import console, report

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

class UnusableCodeError(ValueError):
    pass

class Comment(object):
    def display(self):
        dox = console.color(self.text).rstrip()
        print '{lineno}:\t{dox}'.format(lineno=self.lineno,
                                          dox=dox, )

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
