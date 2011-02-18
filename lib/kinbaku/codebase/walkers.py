""" kinbaku.codebase.walkers
"""
from compiler.ast import Node, Import
def walker(node, level=0, blammo=lambda enoN:None, filters={}):
    "Recurse through a node, pretty-printing it."
    #for condition,response in filters:
    #    if condition(node):
    #        response(node)
    for condition in filters:
        response = filters[condition]
        if condition(node): response(node)
    blammo(node)
    if hasattr(node,'getChildren'):
        for i, child in enumerate(node.getChildren()):
            walker(child, level+1, blammo=blammo, filters=filters)

    """
        #print node,
        test = any(isinstance(child, Node) for child in node.getChildren())
        if test:
        else:
            # None of the children as nodes, simply join their repr on a single
            # line.
            #print type(node),node.__class__
            children=node.getChildren()
    else:
        print '!',node
"""
