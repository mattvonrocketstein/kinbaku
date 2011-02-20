""" kinbaku.codebase.cli
"""
import os
import pprint

from pylint import lint
from pyflakes.scripts.pyflakes import checkPath

from kinbaku.report import report,console
from kinbaku.analysis import combine_word_summary
from kinbaku.analysis import pychecker_helper
from kinbaku.plugin import KinbakuPlugin
from kinbaku.plugin import publish_to_commandline
from kinbaku.util import is_python
from path import path


class CBPlugin(KinbakuPlugin):
    """ """
    @classmethod
    def spawn(kls, path=None, **kargs):
        """ """
        if not path:
            from kinbaku.config import Config
            config = Config.spawn()
            path = config.get('path',None)
        obj = kls(path, gloves_off=True)
        return obj

    @publish_to_commandline
    def search(self, name):
        """ only searches python names """
        result = self._search(name)

        #out=[]
        out={}
        for match1 in result.get('change_map',[]):
            for match2 in match1['matches']:
                fmt_args=dict(lineno=match2['lineno'], line=match2['line'])
                entry = "{lineno}:{line}".format(**fmt_args)
                if match2['real_path'] in out: out[match2['real_path']] += [entry]
                else:                          out[match2['real_path']]  = [entry]

        for k in out:
            print
            print k
            for x in out[k]: print x
            print
        return

    @publish_to_commandline
    def names(self):
        """ shows all names in codebase, sorted by file (AST walker) """
        test        = lambda node: node.__class__.__name__=='Name'
        walkage     = lambda fpath: ast.walk(ast.parse(open(fpath).read()))
        fpath2names = lambda fpath: [ node.id for node in walkage(fpath) if test(node) ]
        return dict([ [fpath, fpath2names(fpath)] for fpath in self.python_files ])


    @publish_to_commandline
    def validate(self,fpath):
        pychecker_helper()

    @publish_to_commandline
    def validate(self, fpath):
        """ validate file """
        #results = self._stats(fpath)
        pyflakes = self.pyflakes
        #results.get('validation')
        for item in self.messages():
            print '\n'.join(str(msg.__class__) for msg in item.messages)

    @publish_to_commandline
    def stats(self,fpath):
        """ Show various statistics for the codebase given codebase.

            Currently, supported metrics include: file count (all files,
            just python files), line count word summary (only words that
            are statistically unlikely) valid booleans for each file

            Coming soon: comment/code ratio, average lines per file,
            average imports per file, total number of classes,
            functions
        """
        results = self._stats(fpath)
        validations = results.get('validation')
        for item in results.items():
            pprint.pprint(item)

    @publish_to_commandline
    def errors(self, fpath):
            return self.messages(fpath,filters='UndefinedName')

    @publish_to_commandline
    def messages(self, fpath, filters=""):
        """ messages from pyflakes: prints message type, file, and pyflakes error to stdout  """
        if isinstance(filters,str): filters=filters.split()
        filters = [x.lower() for x in filters]
        messages = self.pyflakes_messages(fpath)
        _type = lambda m: m.__class__.__name__.lower()
        fmessages = [[msg,_type(msg),_type(msg) in filters ] for msg in messages]
        fmessages = [msg for msg in messages if _type(msg) in filters ]
        for m in fmessages:
            print console.color("{type} {M}".format(type=m.__class__.__name__,M=m)).strip()

    def pyflakes_messages(self, fpath):
        checker = self.pyflakes(fpath).values()[0]
        if isinstance(checker,int): # syntaxerror?
            return [SyntaxError]
        return checker.messages

    def pyflakes(self,fpath=None):
        """ returns a dict of fname:pyflakes.checker """
        if fpath:
            out = dict([[fpath,pychecker_helper(open(fpath).read(), fpath)] ])
        else:
            out = dict([[fpath,pychecker_helper(open(fpath).read(), fpath)] for fpath in self.files(python=True)])
        #print [type(x.messages[0]) for x in out]
        return out

    def _stats(self,fpath):
        """ """
        ws = self.word_summary()
        ws.update(combine_word_summary(ws))
        words_in_all_files = [ ws[fpath].keys() for fpath in ws ]
        pyflakes        = self.pyflakes
        #from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
        return dict( file_count    = self.count_files,
                     py_file_count = self.count_py_files,
                     lines_count   = self.count_lines,
                     word_summary  = ws,
                     validation=pyflakes, )

    @publish_to_commandline
    def shell(self):
        """ """
        #print self.get_changes('${A}=${B}','${A} = ${B}',{}).changes[1].new_contents
        from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()

    @publish_to_commandline
    def files(self, python=False):
        """ returns a list path() objects """
        if not self.pth_root or not os.path.exists(self.pth_root):
            return []
            #raise UnusableCodeError, "nonexistent path {p}".format(p=self.pth_root)
        pth_root = path(self.pth_root)
        if not pth_root.isdir():
            all_files = [pth_root]
        else:
            all_files = pth_root.files()
        if python:
            out = filter(is_python, all_files)
        else:
            out = all_files
        return out
