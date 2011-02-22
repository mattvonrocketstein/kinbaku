""" kinbaku._functools
"""

import os
import inspect

class Bag(object):
    """ a bag of named stuff """
    def __init__(self, **kargs):
        """ """
        [setattr(self,k,v) for k,v in kargs.items()]

class Fingerprint(Bag):
    """ """
    def __str__(self):  return "F:"+str([self.func_name, self.func_filename])
    def __repr__(self): return str(self)


    def __equal__(self,other):
        """ """
        name_match = self.func_name==other.func_name
        path_match = os.path.abspath(self.func_filename)==\
                     os.path.abspath(other.func_filename)
        return  name_match and path_match
    __eq__=__equal__

    @classmethod
    def build_from(kls, func):
        return Fingerprint(func_name=func.func_name,
                           func_filename=inspect.getfile(func),
                           func=func)
