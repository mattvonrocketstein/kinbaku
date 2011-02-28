""" kinbaku._functools
"""

import os
import inspect
from kinbaku._types import Bag

class Fingerprint(Bag):
    """ static representation of a function,
        constructed from either the function itself,
        or frame involving the function """

    def __str__(self):
        D = dict(path=self.func_filename,  line=self.func_line_no,
                 func_name=self.func_name,
                 v=', '.join( [ '='.join(map(str,x)) for x in self.func_vals.items() ] ),
                 retv = self.return_value, )
        return "{path}:{line}\n   {func_name}({v}) -->\n      {retv}".format(**D)

    def __equal__(self,other):
        """ """
        name_match = self.func_name == other.func_name
        path_match = os.path.abspath(self.func_filename)==\
                     os.path.abspath(other.func_filename)
        return  name_match and path_match
    __eq__=__equal__

    @classmethod
    def build_from(kls, func):
        """ """
        return Fingerprint(func_name=func.func_name,
                           func_filename=inspect.getfile(func),
                           func=func)
