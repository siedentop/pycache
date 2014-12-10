import unittest
#from pycallgraph import PyCallGraph
#from pycallgraph.output import GraphvizOutput

from tracer import Tracer

class Callgraph:
    def __init__(self, threaded = False):
        self.threaded = threaded
    
    def execute(self, function, *args, **kwargs):
        output = None
        tracer = Tracer(output, self.threaded)
        with tracer:
            ret = function(*args, **kwargs)

        self.graph = dict()
        for node in tracer.nodes():
            if node.name != '__main__' and not node.name.startswith('tracer'):
                self.graph[node.name] = node.hash
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
        global func_inner
        global func_outer
        cg = Callgraph()
        y = cg.execute(func_outer, 3)
        self.assertEqual(6, y)
        self.assertTrue(cg.unchanged())
        # Change one of the functions   
        def func_inner(x):
            return 3+x
        self.assertEqual(12, func_outer(3))
        self.assertFalse(cg.unchanged())
        # Change back!
        def func_inner(x):
            return x
        self.assertEqual(6, func_outer(3))
        self.assertTrue(cg.unchanged())


if __name__ == '__main__':
    unittest.main()
