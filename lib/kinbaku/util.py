"""
"""
import os, time
import sys, shutil

from path import path

from kinbaku.report import report, console

def _import(name):
    """
        dear __import__,
          I'm breaking up with you.
          You never work the way I expect.

    """
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

def is_string(obj):
    """ the RightWay(tm) to test for stringhood.

         TODO: patch the module to insert also django's
               safe strings?
    """
    return type(obj) in types.StringTypes

def groupby(lst,N):
  """ returns a list with rows of length N, uses as many rows as it takes.
      (the last row is guaranteed to have no more than N elements, but it
       might have fewer, and it won't be padded.)
  """
  out=[]
  while lst:
   try: tmp = lst[:N]; lst=lst[N:]; tmp.reverse()
   except IndexError: break
   tmp.reverse()
   out.append(tmp)
  return out


def is_python(f):
    """ patch this into path obj? """
    return path(f).splitext()[1].endswith('py')

divider=console.draw_line
def remove_recursively(path):
    # windows sometimes raises exceptions instead of removing files
    if os.name == 'nt' or sys.platform == 'cygwin':
          for i in range(12):
            try:
                _remove_recursively(path)
            except OSError, e:
                if e.errno not in (13, 16, 32):
                    raise
                time.sleep(0.3)
            else:
                break
    else:
        _remove_recursively(path)

def _remove_recursively(path):
    if not os.path.exists(path):
        return
    if os.path.isfile(path):
        os.remove(path)
    else:
        shutil.rmtree(path)
