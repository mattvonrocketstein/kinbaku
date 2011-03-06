""" kinbaku._ast
"""
import compiler
from StringIO import StringIO

import sourcecodegen
from peak.util.imports import lazyModule

from kinbaku._sourcecodegen import generate_code
from kinbaku._types import BadDotPath
core = lazyModule('kinbaku.core')

node_has_lineno  = lambda node: hasattr(node,'lineno')
node_is_function = lambda node: isinstance(node,compiler.ast.Function)
node_is_class    = lambda node: isinstance(node,compiler.ast.Class)
node_is_module   = lambda node: isinstance(node,compiler.ast.Module)

from pythoscope.store import code_of # ?

def src2stringio(src_code):
    """ """
    fhandle = StringIO()
    fhandle.write(src_code)
    fhandle.seek(0)
    return fhandle

def walk(node, parent=None, lineage=[],
         test=None, results={}, callback=None):
    """ walker for ast rooted at <node>

          callback will be invoked for node,parent,lineage
          iff test(node) is true.

          the walk is over prematurely if the callback returns
          anything that evaluates to true.

    """
    if node is None: return 99
    elif isinstance(node,(str,int,float,unicode)): pass#rint node
    else:
        if isinstance(node, (list,tuple)):
            out = [ walk(child, parent=node,
                         lineage=lineage+[parent],
                         callback=callback,
                         test=test) for child in node ]
            if any(out):
                return filter(None,out)[0]
        else:
            # make back-links in the node
            node.parent  = parent
            node.lineage = lineage
            children = node.getChildren()
            if test(node):
                result = callback(node, parent, lineage)
                if result:
                    return result

            out = [ walk(child,parent=node,
                         lineage=lineage+[parent],
                         callback=callback,
                         test=test) for child in children]
            if any(out):
                return filter(None, [x for x in out if x])[0]

def walkfunctions(src_code, callback):
    """ static analysis: walk callback over all functions """
    result = None
    kbk_f  = core.KinbakuFile(fhandle=src2stringio(src_code))
    root   = kbk_f.ast
    return walk(root, test=node_is_function, callback=callback, ),root


def dotpath2ast(src_code, dotpath):
    """ static analysis: convert dotpath to python ast """
    odotpath = dotpath
    result = None
    dotpath = dotpath.split('.')

    def callback(node, parent, lineage):
        this_dotpath = [getattr(x,'name') for x in lineage if hasattr(x,'name')]+ [ node.name ]
        if this_dotpath==dotpath:
            return sourcecodegen.generation.generate_code(node),node

    kbk_f = core.KinbakuFile(fhandle=src2stringio(src_code))
    return walk(kbk_f.ast, test=node_is_function, callback=callback, )

def dotpath2obj(src_code, dotpath):
    """ dynamic analysis:
          covert dotpath to python obj
    """
    shadow = {}
    dotpath = dotpath.split('.')
    dotpath.reverse()
    exec(src_code,shadow)
    this = dotpath.pop()
    result = shadow.get(this)
    while dotpath:
        this = dotpath.pop()
        result = getattr(result, this)

    return result

def dotpath2ast_dyn(src_code, func_dotpath):
    """ dynamic analysis:
          covert dotpath to python ast
    """
    return code_of(dotpath2obj(src_code, dotpath))

if __name__=='__main__':
    from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
    x = dotpath2ast('class zoo:\n def f(a,b): return 3', 'zoo.f')
