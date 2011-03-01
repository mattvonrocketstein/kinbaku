""" test__ast

      tests for lib/kinbaku/_ast.py
"""

import unittest
import sourcecodegen
from kinbaku._ast import dotpath2ast
"""
class TestNodeHasLineno(unittest.TestCase):
    def test_node_has_lineno(self):

        # self.assertEqual(expected, node_has_lineno(node))
        assert False # TODO: implement your test here

class TestNodeIsFunction(unittest.TestCase):
    def test_node_is_function(self):

        # self.assertEqual(expected, node_is_function(node))
        assert False # TODO: implement your test here

class TestNodeIsClass(unittest.TestCase):
    def test_node_is_class(self):

        # self.assertEqual(expected, node_is_class(node))
        assert False # TODO: implement your test here

class TestNodeIsModule(unittest.TestCase):
    def test_node_is_module(self):

class TestWalk(unittest.TestCase):
    def test_walk(self):
        # self.assertEqual(expected, walk(node, parent, lineage, test, results, callback))
        assert False # TODO: implement your test here
"""

class TestDotpath2ast(unittest.TestCase):
    def test_dotpath2ast_1(self):
        """ bad dotpaths return None"""
        self.assertTrue(not dotpath2ast("def FUNCTION(a,b): return 3", 'CLASS.FUNCTION'))

    def test_dotpath2ast_2(self):
        """ good dotpaths return sourcecode """
        result,_ = dotpath2ast("def FUNCTION(a,b): return 3", 'FUNCTION')
        self.assertTrue(isinstance(result,str))
        self.assertTrue(len(result))

    def test_dotpath2ast_3(self):
        """ functions inside classes should still be found  """
        print sourcecodegen.__version__
        result,_ = dotpath2ast("class CLASS:\n def FUNCTION(self, a,b):\n 'testing'\n  return 3", 'CLASS.FUNCTION')
        print result
        self.assertTrue(isinstance(result,str))
        self.assertTrue(len(result))

if __name__ == '__main__':
    unittest.main()
