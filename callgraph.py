import unittest
from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput

def func_inner(x):
    print('inner(%s) called' %(x))
    return 2*x

def func_inner2(x):
    pass

def func_outer(x):
    print('outer(%s) called' %(x))
    func_inner2(x)
    return 3*func_inner(x) + 7*func_inner(x)



class Callgraph:
    
    def __init__(self, output_file='callgraph.png'):
        self.graphviz = GraphvizOutput()
        self.graphviz.output_file = output_file
    
    def execute(self, function, *args, **kwargs):
        with PyCallGraph(output=self.graphviz):
            ret = function(*args, **kwargs) # Potentially not a good way in case of generators

        graph = {}

        for edge in self.graphviz.processor.edges():
            if graph.has_key(edge.src_func):
                graph[edge.src_func].add(edge.dst_func)
            else:
                graph[edge.src_func] = set([edge.dst_func])
        print(graph)
        return ret
        
    def __conforms(self, protocol):
        return False
    
    def __eq__(self, other):
        return self.graph == other.graph
    def __ne__(self, other):
        return not self == other

# class CallgraphTest(unittest.TestCase):
#     def testSimple(self):
#         def func_inner(x):
#             return x
#         def func_outer(x):
#             return 2*func_inner(x)
#
#         cg = Callgraph()
#         cg.start()
#         y = func_outer(3)
#         cg.stop()
#         self.assertEqual(y, 6)
#         self.assertEqual(cg.graph, [func_inner, func_outer])
#
#
#     def testRecursive(self):
#         pass
#     def testImportedModule(self):
#         '''If a non-standard-library module is imported, those functions should
#            should also incorporated in the call graph.
#            I don't know what the behaviour should be in this case.
#         '''
#         pass
#     def testCfunctions(self):
#         '''Library functions in C-should also be handled somehow.
#         Not sure how they should be handled.
#         '''
#         pass
#     def testGenerators(self):
#         def func_gen(n):
#             i = 0
#             while i < n:
#                 i += 1
#                 yield i
#         cg = CallGraph()
#         cg.start()
#         self.assertEqual([1, 2, 3], list(func_gen(3)))
#         cg.stop()

if __name__ == '__main__':
    unittest.main()
    # cg = Callgraph()
    # y = cg.execute(func_outer, 3)
    # print('Result: %s' %(y))
