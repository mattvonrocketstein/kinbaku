""" kinbaku.types
"""

class UnusableCodeError(ValueError):
    pass

class Match(object):
    def __str__(self):
        return 'Match_'+str(self.__dict__)

    __repr__=__str__

    def __init__(self, **kargs):
        for k,v in kargs.items(): setattr(self,k,v)
