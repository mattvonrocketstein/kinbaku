""" kinbaku._ast
"""
node_has_lineno = lambda node: hasattr(node,'lineno')
from pythoscope.store import code_of

def walk(node, parent=None, lineage=[],
         test=None, results={}, callback=None):
    """ walker for ast rooted at <node> """
    if node is None: pass
    elif isinstance(node,(str,int,float,unicode)): pass#rint node
    else:
        if isinstance(node, (list,tuple)):
            [ walk(child, parent=node,
                   lineage=lineage+[parent],
                   callback=callback,
                   test=test) for child in node ]
        else:
            children = node.getChildren()
            if test(node):
                callback(node, parent, lineage)
            [ walk(child,parent=node,
                   lineage=lineage+[parent],
                   callback=callback,
                   test=test) for child in children]

if __name__=='__main__':
    from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
