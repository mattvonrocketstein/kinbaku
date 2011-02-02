""" kinbaku.codebase:
      a thin wrapper on rope.base.project for easily working with sandboxes
"""
from kinbaku.codebase.codebase import CodeBase as plugin

if __name__=='__main__':
    import IPython;IPython.Shell.IPShellEmbed(argv=[])()
