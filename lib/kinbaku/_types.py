""" kinbaku.types
"""
from kinbaku.report import console, report

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
