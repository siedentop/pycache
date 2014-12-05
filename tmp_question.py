    import unittest
    from pycallgraph import PyCallGraph
    from pycallgraph.output import GraphvizOutput

    class Callgraph:
        def __init__(self, output_file='callgraph.png'):
            self.graphviz = GraphvizOutput()
            self.graphviz.output_file = output_file
        
        def execute(self, function, *args, **kwargs):
            with PyCallGraph(output=self.graphviz):
                ret = function(*args, **kwargs)

            self.graph = dict()
            for node in self.graphviz.processor.nodes():
                if node.name != '__main__':
                    f = eval(node.name)
                    self.graph[node.name] = hash(f.__code__.co_code)
            return ret

        def unchanged(self):
            '''Checks each function in the callgraph whether it has changed.
            Returns True if all the function have their original code-hash. False otherwise.
            '''
            for func, codehash in self.graph.iteritems():
                f = eval(func)
                if hash(f.__code__.co_code) != codehash:
                    return False
            return True

    def func_inner(x):
        return x
    def func_outer(x):
        return 2*func_inner(x)

    class CallgraphTest(unittest.TestCase):
        def testChanges(self):
            cg = Callgraph()
            y = cg.execute(func_outer, 3)
            self.assertEqual(6, y)
            self.assertTrue(cg.unchanged())
            # Change one of the functions
            def func_inner(x):
                return 3+x
            self.assertFalse(cg.unchanged())
            # Change back!
            def func_inner(x):
                return x
            self.assertTrue(cg.unchanged())


    if __name__ == '__main__':
        unittest.main()


