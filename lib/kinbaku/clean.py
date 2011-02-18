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
    def organize_imports(self, itools, pymodule,
                         unused=True, duplicates=True,
                         selfs=True, sort=True, import_filter=None):
        """ copied from ropes importtools """
        if unused or duplicates:
            module_imports = itools.module_imports(pymodule, import_filter)
            if unused:
                module_imports.remove_unused_imports()
            if duplicates:
                module_imports.remove_duplicates()
            source = module_imports.get_changed_source()
            if source is not None:
                pymodule = itools.pycore.get_string_module(
                    source, pymodule.get_resource())
        #if itools:
        #    pymodule = itools._remove_itools_imports(pymodule, import_filter)
        if sort:
            return self.sort_imports(itools, pymodule, import_filter)
        else:
            return pymodule.source_code

    def sort_imports(self, itools, pymodule, import_filter=None):
        """ copied from ropes importtools """
        module_imports = itools.module_imports(pymodule, import_filter)
        module_imports.sort_imports()
        return module_imports#.get_changed_source()

    @publish_to_commandline
    def imports(self, fpath, inplace=False, changes=False):
        """ cleans and reorganizes module imports for file @fpath,
            displaying result on stdout.  pass the --changes flag
            to see only the import lines and not the whole file.
        """
        if fpath == '-': fpath = stdin2tmpfile(fpath)
        input_file_or_dir = path(fpath)
        with CodeBase(input_file_or_dir, gloves_off=True, workspace=None) as codebase:
            pycore  = codebase.project.pycore
            pymod   = pycore.resource_to_pyobject(codebase>>input_file_or_dir)
            itools = ImportTools(codebase.project.pycore)

            # NOTE: when duplicates is True, moves all package imports to one line
            # NOTE: removes unused imports
            results=self.organize_imports(itools, pymod, duplicates=False)

            results=results.get_changed_source()
            if changes:
                print '\n'.join([line for line in results.split('\n') if line.startswith('from ') or line.startswith('import ')])
            elif inplace:
                fhandle = open(input_file_or_dir,'w')
                fhandle.write(str(results))
                print " + cleaned imports on ",input_file_or_dir
            else:
                print results
plugin = Cleaner

if __name__=='__main__':
    from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
