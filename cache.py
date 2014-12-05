import sqlite3 
import datetime
import os
try:
    import cPickle as pickle
except ImportError:
    import pickle
import unittest

class Cache:
    def __init__(self, config):
        pass
    def keys(self):
        ''' Generator yielding all keys present'''
        raise NotImplementedError
    def add(self, funcname, code_hash, callgraph, 
            args, kwargs, return_values,
            runtime=datetime.datetime.now(), runningtime = None):
        ''' Cache function 'funcname' with the given code_hash, callgraph, arguments/keyword arguments
        and resulting return_values as well as the time it was called.
        (fname+args+kwargs) are used as primary key. 
        A change in code_hash indicates that the old value stored has to be invalidated.
        
        A previous entry with the same funcname but different code_hash or a change in '''
        raise NotImplementedError
    def delete(self):
        raise NotImplementedError
    def get(self, funcname, code_hash, args, kwargs):
        ''' Check for presence of cached value for given parameters.
        Checks that the code_hash hasn't changed as well as that each function
        in the callgraph is the same.
        The key is thus (funcname, args, kwargs), with
        self.callgraph and self.code_hash being checked for changes.
        :return: return_values if function has already been cached. Raises KeyError if no key could be found.
        '''
        raise KeyError
    def invalidate(self):
        ''' Invalidate the complete cache. '''
        raise NotImplementedError

class SqliteCache(Cache):
    def __init__(self, config):
        self.connection = sqlite3.connect(config.file)
        c = self.connection.cursor()
        
        c.execute()


class PickleCache(Cache):
    def __init__(self, config):
        self.picklepath = None # Needed in case config['file'] fails.
        self.picklepath = config['file']
        if os.path.exists(self.picklepath):
            try:
                f = open(self.picklepath, 'rb')
                self.data = pickle.load(f)
            except EOFError as e:
                self.data = dict()
            finally:
                 f.close()
        else:
            self.data = dict()
    def add(self, funcname, code_hash, callgraph,
            args, kwargs, return_values,
            runtime=datetime.datetime.now(), runningtime = None):
        args_hash = hash((args, kwargs))
        if funcname not in self.data:
            self.data[funcname] = {}
        self.data[funcname][args_hash] = {'hash': code_hash, 'callgraph': callgraph,
                               'args': args, 'kwargs': kwargs, 'return_values': return_values,
                               'when': runtime, 'howlong': runningtime}
    def get(self, funcname, code_hash, args, kwargs):
        # TODO: Much of this should be in parent class, as it is generic. A class split into CacheInterface and CacheStorage would do.
        args_hash = hash((args, kwargs))
        cache = self.data[funcname][args_hash] # Raises KeyError if absent
        # Check function for changes and invalidate if necessary
        if cache['hash'] == code_hash and cache['callgraph'].unchanged():
            return cache['return_values']
        elif cache['hash'] != code_hash:
            del self.data[funcname] # Invalidate everything
            raise KeyError('Function %s has changed. Cache invalidated.' %(funcname))
        else: # Only invalidate for (args,kwargs) because callgraph is argument specific.
            del self.data[funcname][args_hash]
            raise KeyError('Function %s has changed for arguments %s/%s. Cache invalidated for these inputs.' %(funcname, args, kwargs))

    def save(self):
        with open(self.picklepath, 'wb') as f:
            pickle.dump(self.data, f, pickle.HIGHEST_PROTOCOL)

    def __del__(self):
        # TODO: __del__ parent
        try:
            self.save()
        except IOError:
            print("Could not save cache!")

class MockCallgraph:
        def __init__(self, graph):
            self.graph = graph
            self.change_flag = False
        def __eq__(self, other):
            return self.graph == other.graph
        def __ne__(self, other):
            return not self == other
        def __getstate__(self):
            return (self.graph, self.change_flag)
        def __setstate__(self,state):
            self.graph = state[0]
            self.change_flag = state[1]
        def unchanged(self):
            return not self.change_flag

def funcA(x):
    return x

def funcB(x):
    return 2*x

class TestPickleCache(unittest.TestCase):
    def setUp(self):
        fname = 'cache.pickle'
        if os.path.exists(fname):
            os.remove(fname)
        config = {'file': fname}
        self.return_values = 5
        self.callgraph = MockCallgraph('original')
        self.uut = PickleCache(config)
        self.args = None
        self.kwargs = None
        self.uut.add(funcname='myfunc', code_hash=123, callgraph=self.callgraph, 
                args=self.args, kwargs=self.kwargs, return_values = self.return_values)
        
    def tearDown(self):
        #del self.uut
        pass
    def test_compare_code_hash(self):
        self.assertEqual(self.return_values, self.uut.get(funcname='myfunc',
                                             code_hash=123, args=self.args,
                                             kwargs=self.kwargs))
        with self.assertRaises(KeyError):
            self.uut.get('myfunc', 124, self.args, self.kwargs)
    def test_compare_funcname(self):
        self.assertEqual(self.return_values, self.uut.get('myfunc', 123, self.args,
                                                          self.kwargs))
        with self.assertRaises(KeyError):
            self.uut.get('notmyfunc', 123, self.args, self.kwargs)
    def test_callgraph_changed(self):
        '''One of the functions in the callgraph has a changed hash'''
        self.assertEqual(self.return_values, self.uut.get('myfunc', 123, self.args,
                                                          self.kwargs))
        self.callgraph.change_flag = True
        #for k, v in self.uut.data['myfunc']:
            #v['callgraph'].change_flag = True
        with self.assertRaises(KeyError):
            self.uut.get('myfunc', 123, self.args, self.kwargs)
        
    def test_args(self):
        with self.assertRaises(KeyError):
            self.uut.get('myfunc', 123, 'args', self.kwargs)
    def test_kwargs(self):
        with self.assertRaises(KeyError):
            self.uut.get('myfunc', 123, self.args, 'kwargs')
    def test_load_from_disk(self):
        config = {'file': self.uut.picklepath}
        del self.uut
        new_cache = PickleCache(config)
        self.assertEqual(self.return_values, new_cache.get('myfunc', 123, self.args, self.kwargs))
        self.uut = new_cache
    
    
    
if __name__=='__main__':
    unittest.main()
    