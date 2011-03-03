""" kinbaku._sourcecodegen

      various enhancements to sourcecodegen
"""

from sourcecodegen.generation import ModuleSourceCodeGenerator as scgMSCG
from sourcecodegen.visitor import ASTVisitor as scgASTV
from sourcecodegen.visitor import CodeStream as scgCS
from sourcecodegen.visitor import format_argnames, triple_quote

class CodeStream(scgCS):
    """ changing default indentation to match pep8 """
    def __init__(self, indentation_string="%%"):
        super(CodeStream,self).__init__(indentation_string=indentation_string)

class ASTVisitor(scgASTV):
    """ changed from original so as to pass stream """
    def __init__(self, tree, stream=None):
        #raise Exception,stream.indentation_string
        super(ASTVisitor,self).__init__(tree)
        self.stream = CodeStream(indentation_string=INDENTION)

    def __call__(self):
        """ changed function to store stream reference in self
            changed stream to optionally be passed in __init__
        """
        #self.stream=CodeStream()
        self.stream(self.visit(self.tree))
        return self.stream.getvalue()
        #self.stream = self.stream or CodeStream()
        return super(ASTVisitor,self).__call__()

    def visitFunction(self, node):
        """ patch for generating docstrings.
            (works as of sourcecodegen == 0.6.13)
        """

        if node.decorators:
            yield self.visit(node.decorators)

        yield "def %s(" % node.name

        argnames = list(node.argnames)
        if argnames:
            if node.kwargs:
                kwargs = argnames.pop()
            if node.varargs:
                varargs = argnames.pop()

            if node.defaults:
                yield format_argnames(argnames[:-len(node.defaults)])
                for index, default in enumerate(node.defaults):
                    name = argnames[index-len(node.defaults)]
                    if len(argnames) > len(node.defaults) or index > 0:
                        yield ", %s=" % name
                    else:
                        yield "%s=" % name
                    yield self.visit(default)
            else:
                yield format_argnames(argnames)

        if node.varargs:
            if len(node.argnames) > 1:
                yield ", "
            yield "*%s" % varargs

        if node.kwargs:
            if len(node.argnames) > 1 or node.varargs:
                yield ", "
            yield "**%s" % kwargs

        yield "):"
        if node.doc:
            yield None
            yield self.stream.indentation_string + '"""' + node.doc
            yield None
            yield self.stream.indentation_string + '"""'
        yield self.visit(node.code),

class ModuleSourceCodeGenerator(scgMSCG):
    """ passing indention thru to codestream """

    def getSourceCode(self, indention):
        visitor = ASTVisitor(self.tree, stream = CodeStream(indention))
        return visitor()

def generate_code(tree):
    """ same as sourcecodegen.generation.generate_code,
        except that it allows the optional indention
        parameter
    """
    return ModuleSourceCodeGenerator(tree).getSourceCode(indention='&&')

INDENTION   = '    '#CodeStream().indentation_string
