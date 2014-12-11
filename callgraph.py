import unittest
from tracer import Tracer

def func_inner(x):
    return 2*x

def func_inner2(x):
    pass

def func_outer(x):
    func_inner2(x)
    return 3*func_inner(x) + 7*func_inner(x)


class Callgraph:
    def __init__(self, threaded = False):
        self.threaded = threaded
    
    def execute(self, function, *args, **kwargs):
        output = None
        tracer = Tracer(output, self.threaded)
        with tracer:
            ret = function(*args, **kwargs)
            
        self.graph = dict()
        self.graph[function.__name__] = hash(function.__code__.co_code)
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

    def __eq__(self, other):
        return self.graph == other.graph
    def __ne__(self, other):
        return not self == other
    def call_set(self):
        ''' Returns `set` of called functions '''
        return set([key for key in self.graph])

class CallgraphTest(unittest.TestCase):
    def testSimple(self):
        global __func_inner, __func_outer
        def __func_inner(x):
            return 1+x
        def __func_outer(x):
            return 2*__func_inner(x)

        cg = Callgraph()
        y = cg.execute(__func_outer, 3)
        self.assertEqual(8, y)
        self.assertEqual(set([__func_inner.__name__, __func_outer.__name__]), cg.call_set())
    
    def testChanges(self):
        global func_inner, func_outer
        def func_inner(x):
            return x
        def func_outer(x):
            return 2*func_inner(x)

        cg = Callgraph()
        y = cg.execute(func_outer, 3)
        self.assertEqual(6, y)
        self.assertTrue(cg.unchanged())
        def func_inner(x):
            return 3+x
        self.assertFalse(cg.unchanged())
        # Change back!
        def func_inner(x):
            return x
        self.assertTrue(cg.unchanged())

    def testRecursive(self):
        def stupid_sum(n):
            assert(n >= 0)
            if n == 0:
                return 0
            else:
                return stupid_sum(n - 1) + 1
        cg = Callgraph()
        self.assertEqual(4, cg.execute(stupid_sum, 4))
        self.assertEqual(set([stupid_sum.__name__]), cg.call_set())
    def testImportedModule(self):
        '''If a non-standard-library module is imported, those functions should
           also be in the call graph.
           I don't know what the behaviour should be in this case.
        '''
        pass
    def testCfunctions(self):
        '''Library functions in C-should also be handled somehow.
        Not sure how they should be handled.
        '''
        pass
    def testGenerators(self):
        def func_gen(n):
            i = 0
            while i < n:
                i += 1
                yield i
        cg = Callgraph()
        res = cg.execute(func_gen, 3)
        self.assertEqual([1, 2, 3], list(res))
        self.assertEqual(set(['func_gen']), cg.call_set())
        
    
    def test_unchanged(self):
        ''' Look at each function in the callgraph and check that its code-hash
        has not changed. 
        '''
        global func_inner, func_outer
        def func_outer(x):
            return 1 + func_inner(x)
        def func_inner(x):
            return 3*x
        cg = Callgraph()
        cg.execute(func_outer, 5)
        self.assertTrue(cg.unchanged())
        def func_inner(x):
            return 2*x
        self.assertTrue(cg.unchanged())
        def func_inner(x):
            return 3*x
        self.assertFalse(cg.unchanged())

    def test_trivial_function(self):
        ''' Assert that trivial functions don't get overlooked.'''
        def trivial(x):
            return x
        def outer_func(x):
            return 2*trivial(x)
        cg = Callgraph()
        self.assertEqual(10, cg.execute(outer_func, 5))
        self.assertEqual(set(['outer_func', 'trivial']), cg.call_set())
        
    def test_multiple_calls(self):
        ''' Call funcA once, then call funcB, make sure funcA does not appear in callgraph of funcB.'''
        pass

if __name__ == '__main__':
    unittest.main()

