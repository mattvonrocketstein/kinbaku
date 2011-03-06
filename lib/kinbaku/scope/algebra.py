""" kinbaku.scope.algebra
"""

from path import path

from pythoscope.generator import name2testname

from kinbaku._sourcecodegen import INDENTION

TEST_PREFIX = name2testname(' ').strip()

class Algebra:
    """ algebraic operators on the test-space """

    @staticmethod
    def abs(fname):
        """ """
        if fname.startswith(TEST_PREFIX):
            return fname[ len(TEST_PREFIX) : ]
        return fname

    def __add__(self, other):
        """ converts to-be-tested-file in the real world
            into the corresponding generated-test-file
            in the shadow world
        """
        assert isinstance(other,str), str(NotImplementedYet)
        _map  = [ [path(tf).basename()[len(TEST_PREFIX):], path(tf).abspath()] for tf in self.tests_files ]
        _map  = dict(_map)
        bname = path(other).basename()
        if bname in _map:
            return _map.get(bname)

    def map(self):
        """ returns {codebase-file:generated-test-file,}

            NOTE: this function is useless before self.make_tests() is called
            see also: self.__add__
        """
        codebasefiles = [ codebasefile.abspath() for codebasefile in self.codebase.files() ]
        codebasefiles = [ [codebasefile, self+codebasefile] for codebasefile in codebasefiles]
        return dict(codebasefiles)

    def __rshift__(self, fpath):
        """ operator to get src code for fpath:

              similar to:
                x = {codebase-file:generate-test-file,}[fpath]
                return open(x).read()

            returns None if it can't map "fpath" to a testfile.
        """
        fpath = path(fpath).abspath()
        out = self.map().get(fpath, None)
        return out and open(out).read()

    def __getitem__(self, slyce):
        """ Examples:

            self[fname:func_name] -->
              src_code for corresponding test function

            self[fname::func_name] -->
              src_code for function test function was generated from
        """
        from pythoscope.generator import find_method_code
        from pythoscope.astbuilder import parse
        if not isinstance(slyce, slice):
            raise Exception,NotImplementedYet
        fpath,y,z = slyce.start,slyce.stop,slyce.step
        if y:
            out = find_method_code(parse(self>>fpath), y)
        elif z:
            out = find_method_code(parse(open(fpath).read()), z)

        if not out:
            raise Exception,NotImplementedYet
        out = str(out).replace('"""',"'").split('\n')
        def x(line):
            if line.strip(): return INDENTION*2 + line
            else: return INDENTION*2+line
        out = [ x(line) for line in out]
        return '\n'.join(out)
