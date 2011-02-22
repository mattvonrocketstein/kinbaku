""" kinbaku._functools
"""

import os
import inspect

class Fingerprint(object):
    def __str__(self):
        return "F:"+str(tuple([self.func_name,self.path]))
    def __repr__(self):
        return str(self)

    def __equal__(self,other):
        return self.func_name==other.func_name and self.path==os.path.abspath(other.path)

    __eq__=__equal__

    @classmethod
    def build_from(kls, func):
        return Fingerprint(func.func_name, inspect.getfile(func), func=func)

    def __init__(self, func_name=None, path=None, func=None):
        """ """
        self.func_name = func_name
        self.path      = os.path.abspath(path)
        self.func      = func
