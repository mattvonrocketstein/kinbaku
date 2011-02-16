""" kinbaku.clean
"""
import sys
from path import path
import tempfile

from rope.refactor.importutils import ImportTools, importinfo, add_import

from kinbaku.report import console, report
from kinbaku.plugin import KinbakuPlugin, publish_to_commandline
from kinbaku.codebase import plugin as CodeBase
from kinbaku._types import Comment

def stdin2tmpfile(fpath):
    """ """
    fname = tempfile.mktemp()+'.py'
    fhandle = open(fname,'w')
    fhandle.writelines(sys.stdin.readlines())
    fhandle.close()
    return fname

class Cleaner(KinbakuPlugin):
    """ """

    @classmethod
    def spawn(kls, **kargs):
        return Cleaner()

    @publish_to_commandline
    def whitespace(self, fpath):
        """ trims trailing whitespace (newlines are untouched) """
        if fpath=='-': fpath=stdin2tmpfile(fpath)
        print ''.join([x.rstrip()+'\n' for x in open(fpath).readlines()])

    @publish_to_commandline
    def pep8(self, fpath):
        """ pep8ify's file a @fpath, displaying result on stdout """
        if fpath=='-': fpath=stdin2tmpfile(fpath)
        ## "a=b" --> "a = b"
        with CodeBase(fpath, gloves_off=True, workspace=None) as codebase:
            codebase.snapshot()
            changes = codebase.get_changes('${A}=${B}','${A} = ${B}',{})
            changes = changes.changes
            assert len(changes)==1
            changes = changes[0]
            b1 = path(changes.resource.real_path).basename()
            b2 = path(fpath).basename()
            assert b1==b2, "NOT EQUAL:"+str([b1,b2])
            print changes.new_contents.strip()
            #from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
        pass

    @publish_to_commandline
    def imports(self, fpath, changes=False):
        """ cleans and reorganizes module imports for file @fpath,
            displaying result on stdout.  pass the --changes flag
            to see only the import lines and not the whole file.
        """
        if fpath == '-': fpath = stdin2tmpfile(fpath)
        input_file_or_dir = path(fpath)
        with CodeBase(input_file_or_dir, gloves_off=True, workspace=None) as codebase:
            pycore = codebase.project.pycore
            pymod  = pycore.resource_to_pyobject(codebase>>input_file_or_dir)
            x = ImportTools(codebase.project.pycore).organize_imports(pymod, unused=False)
            print x

plugin = Cleaner
