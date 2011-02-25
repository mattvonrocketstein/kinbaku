""" kinbaku.pygrep

    ways of generating subsections of python source
"""

def pygrep(fpath, instruction,raw_text=False):
    """ """
    # HACK: uses ropes' import cleaning refactor
    #       returns a string consisting of only import lines
    if instruction=='imports':
        from StringIO import StringIO
        from kinbaku.clean import Cleaner
        z = StringIO()
        Cleaner()._imports(fpath, inplace=False, changes=True, stream=z)
        if raw_text:
            z.seek(0);
            return z.read()
        else:
            return z
    else:
        raise Exception, "Unrecognized instruction"
