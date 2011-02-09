""" kinbaku.codebase:
      a thin wrapper on rope.base.project for easily working with sandboxes
"""
from kinbaku.codebase.codebase import CodeBase as plugin

if __name__=='__main__':
    cb=plugin('/home/matt/code/kinbaku/codebox',gloves_off=True, workspace='testing')
    cb.snapshot()
    cb.has_changed('codebox/tools.py')
    #import IPython;IPython.Shell.IPShellEmbed(argv=[])()
