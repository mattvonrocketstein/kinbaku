""" kinbaku.pygrep

    ways of generating subsections of python source
"""
from StringIO import StringIO
from kinbaku.clean import Cleaner

class pygrep(object):
    """ """

    def imports(self, fpath, raw_text):
        """ HACK: uses ropes' import cleaning refactor returns
                  a string consisting of only import lines
        """
        result = StringIO()
        Cleaner()._imports(fpath, inplace=False, changes=True, stream=result)
        if raw_text:
            result.seek(0);
            return result.read()
        else:
            return result

    def __call__(self, fpath, instruction, raw_text=False):
        """ """
        handler = getattr(self,instruction,None)
        if handler:
            return handler(fpath, raw_text=raw_text)
        else:
            raise Exception, "Unrecognized instruction"
pygrep = pygrep()
